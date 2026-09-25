// crackATT v3.3 for AutoTouch 8.5.5

#import <Foundation/Foundation.h>
#import <UIKit/UIKit.h>
#import <substrate.h>
#include <dlfcn.h>

@interface CommandServer_907239 : NSObject
@end
@interface Global_983499 : NSObject
@end
@interface JSEngine : NSObject
@end
@interface PlayingManager_932730 : NSObject
@end
@interface Alert : NSObject
@end
@interface ATTweakClient : NSObject
@end
@interface SettingsViewController : UIViewController
@end

static BOOL (*orig_validateLicense_108147)(id *errorOut);
static BOOL (*orig__validateLicense_108147)(id *errorOut);
static BOOL (*orig__validateLicenseFromKey_565433)(id key);
static long long (*orig_downloadLicenseSynchronously_552911)(int, void **, void **);

static long long replaced_downloadLicenseSynchronously_552911(int flag, void **planOut, void **errorOut) {
    if (errorOut)
        *errorOut = NULL;
    return 1;
}

static BOOL replaced_validateLicense_108147(id *errorOut) {
    return YES;
}

static BOOL replaced__validateLicenseFromKey_565433(id key) {
    return YES;
}

static BOOL crack_is_license_text(NSString *text) {
    if (![text isKindOfClass:[NSString class]] || text.length == 0)
        return NO;
    static NSArray<NSString *> *needles;
    static dispatch_once_t once;
    dispatch_once(&once, ^{
        needles = @[
            @"License is needed",
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

static void install_validate_hooks(void) {
    void *sym;

    sym = dlsym(RTLD_DEFAULT, "validateLicense_108147");
    if (sym && sym != (void *)replaced_validateLicense_108147) {
        MSHookFunction(sym, (void *)replaced_validateLicense_108147, (void **)&orig_validateLicense_108147);
    }

    sym = dlsym(RTLD_DEFAULT, "_validateLicense_108147");
    if (sym && sym != (void *)replaced_validateLicense_108147) {
        MSHookFunction(sym, (void *)replaced_validateLicense_108147, (void **)&orig__validateLicense_108147);
    }

    sym = dlsym(RTLD_DEFAULT, "_validateLicenseFromKey_565433");
    if (sym && sym != (void *)replaced__validateLicenseFromKey_565433) {
        MSHookFunction(sym, (void *)replaced__validateLicenseFromKey_565433, (void **)&orig__validateLicenseFromKey_565433);
    }

    sym = dlsym(RTLD_DEFAULT, "_downloadLicenseSynchronously_552911");
    if (!sym)
        sym = dlsym(RTLD_DEFAULT, "downloadLicenseSynchronously_552911");
    if (sym && sym != (void *)replaced_downloadLicenseSynchronously_552911) {
        MSHookFunction(sym, (void *)replaced_downloadLicenseSynchronously_552911, (void **)&orig_downloadLicenseSynchronously_552911);
    }
}

static void schedule_validate_hook_retries(void) {
    install_validate_hooks();
    for (int i = 1; i <= 6; i++) {
        dispatch_after(dispatch_time(DISPATCH_TIME_NOW, (int64_t)(i * NSEC_PER_SEC)), dispatch_get_main_queue(), ^{
            install_validate_hooks();
        });
    }
}

%hook CommandServer_907239
- (void)setupTimer_240358 { return; }
- (void)licenseLimitTimeout_120300 { return; }
- (void)licenseCoolDown_266971 { return; }
- (void)check_929132 { return; }
- (void)outputLicenseTimeout_847601 { return; }
- (BOOL)isLicensed { return YES; }
- (BOOL)licensed { return YES; }
- (BOOL)licenseTimeout { return NO; }
%end

%hook Global_983499
- (void)setupTimer_167855 { return; }
- (void)licenseLimitTimeout_552565 { return; }
- (BOOL)isLicensed { return YES; }
- (BOOL)licensed { return YES; }
- (BOOL)licenseTimeout { return NO; }
%end

%hook JSEngine
+ (void)setupTimer { return; }
+ (void)licenseLimitTimeout { return; }
+ (void)alertForProVersion { return; }
%end

%hook PlayingManager_932730
- (void)stopAllPlayings_309465 { return; }
- (void)stopAllPlayings { return; }
%end

%hook ATTweakClient
- (BOOL)downloadLicense:(NSError **)error {
    if (error)
        *error = nil;
    return YES;
}
%end

%hook SettingsViewController
- (void)checkLicenseStatus {
    %orig;
    UILabel *label = [self valueForKey:@"licenseStatusLabel"];
    if ([label isKindOfClass:[UILabel class]])
        label.text = @"Licensed";
}
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
    schedule_validate_hook_retries();
    NSLog(@"[crackATT v3.3] loaded in %@", [[NSBundle mainBundle] bundleIdentifier]);
}
