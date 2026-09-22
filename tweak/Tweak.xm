// crackATT v2 for AutoTouch 8.5.5

#import <Foundation/Foundation.h>
#import <UIKit/UIKit.h>

@interface CommandServer_907239 : NSObject
@end
@interface Global_983499 : NSObject
@end
@interface JSEngine : NSObject
@end
@interface PlayingManager_932730 : NSObject
@end

%hook CommandServer_907239
- (void)setupTimer_240358 { return; }
- (void)licenseLimitTimeout_120300 { return; }
- (void)licenseCoolDown_266971 { return; }
- (void)check_929132 { return; }
%end

%hook Global_983499
- (void)setupTimer_167855 { return; }
- (void)licenseLimitTimeout_552565 { return; }
%end

%hook JSEngine
+ (void)alertForProVersion { return; }
%end

%hook PlayingManager_932730
- (void)stopAllPlayings { return; }
%end

%ctor {
    NSLog(@"[crackATT v2] loaded for AutoTouch 8.5.5");
}
