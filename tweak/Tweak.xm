// crackATT v2.1 for AutoTouch 8.5.5

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

static BOOL (*orig_validateLicense_108147)(id *errorOut);
static BOOL (*orig__validateLicense_108147)(id *errorOut);
static BOOL (*orig__validateLicenseFromKey_565433)(id key);

static BOOL replaced_validateLicense_108147(id *errorOut) {
    return YES;
}

static BOOL replaced__validateLicenseFromKey_565433(id key) {
    return YES;
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
}

%hook CommandServer_907239
- (void)setupTimer_240358 { return; }
- (void)licenseLimitTimeout_120300 { return; }
- (void)licenseCoolDown_266971 { return; }
- (void)check_929132 { return; }
- (BOOL)isLicensed { return YES; }
- (BOOL)licensed { return YES; }
%end

%hook Global_983499
- (void)setupTimer_167855 { return; }
- (void)licenseLimitTimeout_552565 { return; }
- (BOOL)isLicensed { return YES; }
- (BOOL)licensed { return YES; }
%end

%hook JSEngine
+ (void)alertForProVersion { return; }
%end

%hook PlayingManager_932730
- (void)stopAllPlayings_309465 { return; }
%end

%hook Alert
+ (void)showAlert:(id)message {
    if ([message isKindOfClass:[NSString class]]) {
        NSString *text = (NSString *)message;
        if ([text containsString:@"License is needed"] || [text containsString:@"License Required"])
            return;
    }
    %orig;
}

+ (void)showAlertWithTitle:(id)title message:(id)message buttonTitle:(id)buttonTitle {
    if ([message isKindOfClass:[NSString class]]) {
        NSString *text = (NSString *)message;
        if ([text containsString:@"License is needed"] || [text containsString:@"License Required"])
            return;
    }
    %orig;
}
%end

%ctor {
    install_validate_hooks();
    dispatch_after(dispatch_time(DISPATCH_TIME_NOW, (int64_t)(2 * NSEC_PER_SEC)), dispatch_get_main_queue(), ^{
        install_validate_hooks();
    });
    NSLog(@"[crackATT v2.1] loaded for AutoTouch 8.5.5");
}
