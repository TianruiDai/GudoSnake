[app]

title = Gudo Snake
package.name = gudosnake
package.domain = org.gudosnake

source.dir = .
source.include_exts = py,png,jpg,jpeg,yaml,mp3

source.exclude_patterns = demo.py,SnakeGame.spec,build/*,.buildozer/*,bin/*,.git/*,build-android.sh,build-android.ps1,Dockerfile,signing/*.keystore,signing/keystore.properties

version = 1.0.0

requirements = python3,hostpython3,pyjnius,pyyaml,pygame-ce

icon.filename = %(source.dir)s/assets/icon.png
presplash.filename = %(source.dir)s/assets/presplash.png
icon.adaptive_foreground.filename = %(source.dir)s/assets/icon_foreground.png
icon.adaptive_background.filename = %(source.dir)s/assets/icon_background.png

orientation = portrait
fullscreen = 1

android.api = 34
android.minapi = 21
android.ndk_api = 21
android.accept_sdk_license = True
android.archs = arm64-v8a, armeabi-v7a
android.manifest.orientation = portrait

p4a.branch = develop
p4a.local_recipes = ./p4a-recipes
p4a.bootstrap = sdl2

# Release signing (filled temporarily by scripts/build-release.sh)
# android.keystore = %(source.dir)s/signing/gudosnake-release.keystore
# android.keystore_password = YOUR_PASSWORD
# android.keyalias = gudosnake
# android.keyalias_password = YOUR_PASSWORD

[buildozer]

log_level = 2
warn_on_root = 1
