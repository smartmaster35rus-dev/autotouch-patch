// crackATT v2.1 for AutoTouch 8.5.5

#import <Foundation/Foundation.h>
#import <UIKit/UIKit.h>

BOOL validateLicense_108147(id *errorOut);
BOOL _validateLicense_108147(id *errorOut);
BOOL _validateLicenseFromKey_565433(id key);

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

%hookf(BOOL, validateLicense_108147, id *errorOut) {
    return YES;
}

%hookf(BOOL, _validateLicense_108147, id *errorOut) {
    return YES;
}

%hookf(BOOL, _validateLicenseFromKey_565433, id key) {
    return YES;
}

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
    NSLog(@"[crackATT v2.1] loaded for AutoTouch 8.5.5");
}
