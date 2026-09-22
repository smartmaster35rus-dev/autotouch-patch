// crackATT v2 for AutoTouch 8.5.5
// Based on IDA Pro 9.4 decompile of ATTweak.dylib
//
// License chain (confirmed):
//   CommandServer_907239.setupTimer_240358  -> NSTimer 120.0s -> licenseLimitTimeout_120300
//   Global_983499.setupTimer_167855       -> NSTimer 120.0s -> licenseLimitTimeout_552565
//   licenseLimitTimeout_552565            -> PlayingManager_932730 stopAllPlayings + alert
//   JSEngine.alertForProVersion            -> JSEngine stop + alert UI
//
// Old crackATT v1 hooked Global/startLicenseLimitTimer/objectFromJSONString only -> insufficient.

#import <Foundation/Foundation.h>
#import <UIKit/UIKit.h>

#define CRACK_NOOP \
    %orig; \
    return;

#define CRACK_HOOK_LICENSE(ClassName) \
    %hook ClassName \
    - (void)setupTimer_240358 { return; } \
    - (void)setupTimer_167855 { return; } \
    - (void)licenseLimitTimeout_120300 { return; } \
    - (void)licenseLimitTimeout_552565 { return; } \
    - (void)licenseLimitTimeout { return; } \
    - (void)licenseCoolDown_266971 { return; } \
    - (void)check_929132 { return; } \
    - (BOOL)isLicensed { return YES; } \
    - (BOOL)licensed { return YES; } \
    - (void)alertForProVersion { return; } \
    - (id)getLicense { return @{@"licensed":@YES, @"valid":@YES, @"expired":@NO}; } \
    %end

CRACK_HOOK_LICENSE(CommandServer_907239)
CRACK_HOOK_LICENSE(Global_983499)

// Legacy names (7.x compatibility)
CRACK_HOOK_LICENSE(Global)

%hook JSEngine
+ (void)setupTimer { return; }
+ (void)licenseLimitTimeout { return; }
+ (void)alertForProVersion { return; }
+ (void)stop { /* allow scripts */ }
%end

%hook PlayingManager_932730
- (void)stopAllPlayings { return; }
- (BOOL)hasAnyPlaying { return %orig; }
%end

%ctor {
    NSLog(@"[crackATT v2] loaded for AutoTouch 8.5.5");
}
