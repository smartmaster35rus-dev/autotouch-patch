// crackATT for AutoTouch 8.0.11 (inputtext) — use with binary-patched ATTweak.dylib

#import <Foundation/Foundation.h>
#import <UIKit/UIKit.h>
#import <objc/runtime.h>

@interface CommandServer : NSObject
@end
@interface Spring : NSObject
@end
@interface JSEngine : NSObject
@end
@interface JSExtension : NSObject
@end
@interface Alert : NSObject
@end
@interface ATTweakClient : NSObject
@end
@interface LicenseManager : NSObject
@end
@interface LicenseViewController : UIViewController
@end
@interface SettingsViewController : UIViewController
@end

static BOOL crack_is_license_text(NSString *text) {
    if (![text isKindOfClass:[NSString class]] || text.length == 0)
        return NO;
    static NSArray<NSString *> *needles;
    static dispatch_once_t once;
    dispatch_once(&once, ^{
        needles = @[
            @"License is needed",
            @"launch script automatically",
            @"License Required",
            @"AutoTouch License",
            @"free version of AutoTouch",
            @"few minutes",
            @"You need a license",
            @"License is expired",
            @"License is unverified",
            @"License is not verified",
        ];
    });
    for (NSString *needle in needles) {
        if ([text rangeOfString:needle options:NSCaseInsensitiveSearch].location != NSNotFound)
            return YES;
    }
    return NO;
}

static void crack_force_licensed_ivar(id obj) {
    if (!obj)
        return;
    Class cls = object_getClass(obj);
    const char *names[] = {"_licensed", "licensed", "_licenseChecked", NULL};
    for (int i = 0; names[i]; i++) {
        Ivar iv = class_getInstanceVariable(cls, names[i]);
        if (iv) {
            const char *type = ivar_getTypeEncoding(iv);
            if (type && type[0] == 'B')
                object_setIvar(obj, iv, (void *)YES);
            else
                object_setIvar(obj, iv, (__bridge id)kCFBooleanTrue);
        }
    }
}

static void crack_apply_licensed_ui(UIViewController *self) {
    if (!self)
        return;
    for (NSString *key in @[@"licenseStatusLabel", @"licenseLabel", @"_licenseLabel"]) {
        id label = [self valueForKey:key];
        if ([label isKindOfClass:[UILabel class]]) {
            ((UILabel *)label).text = @"Licensed";
            return;
        }
    }
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

%hook JSEngine
+ (void)alertForProVersion { return; }
+ (void)licenseLimitTimeout { return; }
%end

%hook JSExtension
+ (id)getLicense {
    return @"Licensed";
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
    if (crack_is_license_text((NSString *)message))
        return;
    %orig;
}
+ (void)showAlertWithTitle:(id)title message:(id)message buttonTitle:(id)buttonTitle {
    if (crack_is_license_text((NSString *)title) || crack_is_license_text((NSString *)message))
        return;
    %orig;
}
%end

%ctor {
    NSLog(@"[crackATT 8.0.11] loaded in %@", [[NSBundle mainBundle] bundleIdentifier]);
}
