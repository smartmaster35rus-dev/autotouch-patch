// crackATT v2 for AutoTouch 8.5.5

#import <Foundation/Foundation.h>
#import <UIKit/UIKit.h>

@interface CommandServer_907239 : NSObject
@end
@interface Global_983499 : NSObject
@end
@interface Global : NSObject
@end
@interface JSEngine : NSObject
@end
@interface PlayingManager_932730 : NSObject
@end

%hook CommandServer_907239
- (void)setupTimer_240358 { return; }
- (void)setupTimer_167855 { return; }
- (void)licenseLimitTimeout_120300 { return; }
- (void)licenseLimitTimeout_552565 { return; }
- (void)licenseLimitTimeout { return; }
- (void)licenseCoolDown_266971 { return; }
- (void)check_929132 { return; }
- (BOOL)isLicensed { return YES; }
- (BOOL)licensed { return YES; }
- (void)alertForProVersion { return; }
- (id)getLicense { return @{@"licensed":@YES, @"valid":@YES, @"expired":@NO}; }
%end

%hook Global_983499
- (void)setupTimer_240358 { return; }
- (void)setupTimer_167855 { return; }
- (void)licenseLimitTimeout_120300 { return; }
- (void)licenseLimitTimeout_552565 { return; }
- (void)licenseLimitTimeout { return; }
- (void)licenseCoolDown_266971 { return; }
- (void)check_929132 { return; }
- (BOOL)isLicensed { return YES; }
- (BOOL)licensed { return YES; }
- (void)alertForProVersion { return; }
- (id)getLicense { return @{@"licensed":@YES, @"valid":@YES, @"expired":@NO}; }
%end

%hook Global
- (void)setupTimer_240358 { return; }
- (void)setupTimer_167855 { return; }
- (void)licenseLimitTimeout_120300 { return; }
- (void)licenseLimitTimeout_552565 { return; }
- (void)licenseLimitTimeout { return; }
- (void)licenseCoolDown_266971 { return; }
- (void)check_929132 { return; }
- (BOOL)isLicensed { return YES; }
- (BOOL)licensed { return YES; }
- (void)alertForProVersion { return; }
- (id)getLicense { return @{@"licensed":@YES, @"valid":@YES, @"expired":@NO}; }
- (void)startLicenseLimitTimer { return; }
- (void)init { %orig; }
%end

%hook JSEngine
+ (void)setupTimer { return; }
+ (void)licenseLimitTimeout { return; }
+ (void)alertForProVersion { return; }
%end

%hook PlayingManager_932730
- (void)stopAllPlayings { return; }
%end

%ctor {
    NSLog(@"[crackATT v2] loaded for AutoTouch 8.5.5");
}
