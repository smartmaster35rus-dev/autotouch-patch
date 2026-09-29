// crackATT for AutoTouch 8.0.11 (inputtext) — hybrid with binary-patched ATTweak.dylib

#import <Foundation/Foundation.h>
#import <UIKit/UIKit.h>
#import <objc/runtime.h>
#import <objc/message.h>

@interface CommandServer : NSObject
@end
@interface Spring : NSObject
@end
@interface JSEngine : NSObject
@end
@interface JSExtension : NSObject
@end
@interface AutoLaunchManager : NSObject
@end
@interface Alert : NSObject
@end
@interface TimerManager : NSObject
@end
@interface ATTweakClient : NSObject
@end
@interface LicenseManager : NSObject
@end
@interface LicenseViewController : UIViewController
@end
@interface SettingsViewController : UIViewController
@end

static BOOL crack_text_mentions_license(NSString *text) {
    if (![text isKindOfClass:[NSString class]] || text.length == 0)
        return NO;
    return [text rangeOfString:@"license" options:NSCaseInsensitiveSearch].location != NSNotFound
        || [text rangeOfString:@"licence" options:NSCaseInsensitiveSearch].location != NSNotFound
        || [text rangeOfString:@"Unlicensed" options:NSCaseInsensitiveSearch].location != NSNotFound;
}

static BOOL crack_is_license_text(NSString *text) {
    if (![text isKindOfClass:[NSString class]] || text.length == 0)
        return NO;
    if (crack_text_mentions_license(text))
        return YES;
    static NSArray<NSString *> *needles;
    static dispatch_once_t once;
    dispatch_once(&once, ^{
        needles = @[
            @"launch script automatically",
            @"run script by timer",
            @"few minutes",
            @"free version of AutoTouch",
            @"without limitations",
        ];
    });
    for (NSString *needle in needles) {
        if ([text rangeOfString:needle options:NSCaseInsensitiveSearch].location != NSNotFound)
            return YES;
    }
    return NO;
}

static BOOL crack_should_block_alert(NSString *title, NSString *message) {
    return crack_is_license_text(title) || crack_is_license_text(message);
}

static void crack_force_licensed_ivar(id obj) {
    if (!obj)
        return;
    Class cls = object_getClass(obj);
    const char *boolNames[] = {"_licenseChecked", NULL};
    const char *objNames[] = {"_licensed", "licensed", NULL};
    for (int i = 0; boolNames[i]; i++) {
        Ivar iv = class_getInstanceVariable(cls, boolNames[i]);
        if (iv)
            *((BOOL *)((uint8_t *)(__bridge void *)obj + ivar_getOffset(iv))) = YES;
    }
    Ivar timeoutIv = class_getInstanceVariable(cls, "_licenseTimeout");
    if (timeoutIv)
        *((BOOL *)((uint8_t *)(__bridge void *)obj + ivar_getOffset(timeoutIv))) = NO;
    for (int i = 0; objNames[i]; i++) {
        Ivar iv = class_getInstanceVariable(cls, objNames[i]);
        if (iv)
            object_setIvar(obj, iv, (__bridge id)kCFBooleanTrue);
    }
}

static void crack_refresh_license_state(void) {
    for (NSString *name in @[@"CommandServer", @"Spring"]) {
        Class cls = objc_getClass(name.UTF8String);
        if (!cls)
            continue;
        SEL sel = sel_registerName("sharedInstance");
        if (![cls respondsToSelector:sel])
            continue;
        id inst = ((id (*)(id, SEL))objc_msgSend)(cls, sel);
        crack_force_licensed_ivar(inst);
    }
}

static void crack_apply_licensed_ui(UIViewController *vc) {
    if (!vc)
        return;
    for (NSString *key in @[@"licenseStatusLabel", @"licenseLabel", @"_licenseLabel"]) {
        id label = [vc valueForKey:key];
        if ([label isKindOfClass:[UILabel class]]) {
            ((UILabel *)label).text = @"Licensed";
            return;
        }
    }
}

static BOOL crack_armor_process(void) {
    NSString *bid = [[NSBundle mainBundle] bundleIdentifier];
    return [bid isEqualToString:@"com.apple.springboard"]
        || [bid isEqualToString:@"com.apple.backboardd"]
        || [bid isEqualToString:@"me.autotouch.AutoTouch.ios8"];
}

static BOOL crack_vc_is_license_alert(UIViewController *vc) {
    if (![vc isKindOfClass:[UIAlertController class]])
        return NO;
    if (crack_armor_process())
        return YES;
    UIAlertController *alert = (UIAlertController *)vc;
    return crack_should_block_alert(alert.title, alert.message);
}

%hook CommandServer
- (id)init {
    id r = %orig;
    crack_force_licensed_ivar(r);
    return r;
}
- (void)suYYKTj6MHk { return; }
- (void)licenseLimitTimeout { return; }
- (void)licenseCoolDown { return; }
- (void)outputLicenseTimeout { return; }
- (void)check { return; }
- (BOOL)isLicensed { return YES; }
- (BOOL)licensed { return YES; }
- (BOOL)licenseTimeout { return NO; }
%end

%hook Spring
- (id)init {
    id r = %orig;
    crack_force_licensed_ivar(r);
    return r;
}
- (void)suYYKTj6MHk { return; }
- (void)licenseLimitTimeout { return; }
- (BOOL)isLicensed { return YES; }
- (BOOL)licensed { return YES; }
- (BOOL)licenseTimeout { return NO; }
%end

%hook AutoLaunchManager
- (void)loadAndSync {
    crack_refresh_license_state();
    %orig;
}
- (void)sync {
    crack_refresh_license_state();
    %orig;
}
- (void)launch {
    crack_refresh_license_state();
    %orig;
}
- (void)start:(id)arg {
    crack_refresh_license_state();
    %orig;
}
%end

%hook TimerManager
- (void)doPlay:(id)arg {
    crack_refresh_license_state();
    %orig;
}
%end

%hook JSEngine
+ (void)alertForProVersion { return; }
%end

%hook JSExtension
+ (id)getLicense {
    return @{@"licensed": @YES, @"valid": @YES, @"expired": @NO, @"status": @"Licensed"};
}
%end

%hook ATTweakClient
- (BOOL)downloadLicense:(NSError **)error {
    if (error)
        *error = nil;
    return YES;
}
- (BOOL)downloadLicenseFile:(id)path {
    return YES;
}
- (BOOL)downloadLicenseFile:(id)path slient:(BOOL)silent {
    return YES;
}
- (BOOL)licensed {
    return YES;
}
%end

%hook LicenseManager
- (void)downloadLicenseAsync:(id)success fail:(id)fail {
    if (success) {
        void (^ok)(long long) = success;
        ok(1);
        return;
    }
    %orig;
}
- (BOOL)downloadLicenseFile:(id)path {
    return YES;
}
- (BOOL)downloadLicenseFile:(id)path slient:(BOOL)silent {
    return YES;
}
%end

%hook LicenseViewController
- (void)viewWillAppear:(BOOL)animated {
    %orig;
    crack_apply_licensed_ui(self);
}
- (BOOL)licensed { return YES; }
%end

%hook SettingsViewController
- (void)viewWillAppear:(BOOL)animated {
    %orig;
    crack_apply_licensed_ui(self);
}
- (BOOL)licensed { return YES; }
%end

%hook Alert
+ (void)showAlert:(id)message {
    if (crack_armor_process() || crack_is_license_text((NSString *)message))
        return;
    %orig;
}
+ (void)showAlertWithTitle:(id)title message:(id)message buttonTitle:(id)buttonTitle {
    if (crack_armor_process() || crack_should_block_alert((NSString *)title, (NSString *)message))
        return;
    %orig;
}
%end

%hook UIAlertController
+ (instancetype)alertControllerWithTitle:(NSString *)title message:(NSString *)message preferredStyle:(UIAlertControllerStyle)style {
    if (crack_armor_process() || crack_should_block_alert(title, message))
        return nil;
    return %orig;
}
- (instancetype)initWithTitle:(NSString *)title message:(NSString *)message preferredStyle:(UIAlertControllerStyle)style {
    if (crack_armor_process() || crack_should_block_alert(title, message))
        return nil;
    return %orig;
}
%end

%hook UIViewController
- (void)presentViewController:(UIViewController *)viewControllerToPresent animated:(BOOL)flag completion:(void (^)(void))completion {
    if (crack_vc_is_license_alert(viewControllerToPresent))
        return;
    %orig;
}
%end

%ctor {
    crack_refresh_license_state();
    dispatch_after(dispatch_time(DISPATCH_TIME_NOW, (int64_t)(2 * NSEC_PER_SEC)), dispatch_get_main_queue(), ^{
        crack_refresh_license_state();
    });
    NSLog(@"[crackATT 8.0.11 v3 armor] loaded in %@", [[NSBundle mainBundle] bundleIdentifier]);
}
