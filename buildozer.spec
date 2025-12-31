[app]
title = Snake Game
package.name = snakegame
package.domain = org.vishwanth

source.dir = .
source.include_exts = py

version = 0.1

requirements = python3,kivy

orientation = portrait

fullscreen = 1

android.permissions = INTERNET

android.api = 31
android.minapi = 21
android.ndk = 25b
android.sdk = 31

android.archs = arm64-v8a,armeabi-v7a

[buildozer]
log_level = 2
warn_on_root = 1
