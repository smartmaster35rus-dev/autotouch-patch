ARCHS = arm64
TARGET = iphone:clang:16.5:14.0

INSTALL_TARGET_PROCESSES = SpringBoard

include $(THEOS)/makefiles/common.mk

TWEAK_NAME = crackATT

crackATT_FILES = Tweak.xm
crackATT_CFLAGS = -fobjc-arc

include $(THEOS)/makefiles/tweak.mk

after-all::
	@echo "Built: $(THEOS_OBJ_DIR)/crackATT.dylib"
