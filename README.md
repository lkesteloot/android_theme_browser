
# Android Theme Browser

This Python script analyzes the `themes.xml` resource files of
an Android project, the appcompat library, and the SDK, and generates
a dump of all attributes. This is useful for figuring out what
attributes are set by each theme. It also shows each theme's
ancestry and each item's ancestry.

The output can be filtered to one theme, one attribute, or
a max API version. An API "sweep" can also be done to show
how an attribute changes across all API values.

# Usage

Run the script, specifying a list of resource directories. These
can include the resource directory of your app, of the
[support files](https://github.com/aosp-mirror/platform_frameworks_support),
or the platform files. For example:

    python android_theme_browser.py \
        ~/my_project/android/app/src/main/res \
        ~/others/platform_frameworks_support/v7/appcompat/res \
        ~/Library/Android/sdk/platforms/android-27/data/res

This will dump all themes that were found, and all their attributes.
For each theme you'll see the theme name and pathname, its ancestry
(parent themes all the way up to `android:Theme`), and all of
its attributes. For each attribute you'll see the name and
its ancestry (the values it had in the theme's ancestry).

To dump only one theme, add the `--theme` flag:

    --theme android:Theme.Light

To dump only one attribute, add the `--attr` flag:

    --attr android:actionBarStyle

By the default the script uses all themes found, including
overrides for recent API versions. Add the `--api` flag to
limit the search to an older API. For example, to look at
how these themes would look to Android API 20, add the
flag:

    --api 20

To look at how a specific attribute changes over all APIs,
specify the theme and attribute and use `all` for the API:

    --theme Theme.AppCompat.Light.NoActionBar --attr android:listViewStyle --api all

which generates this output:

     1: @style/Widget.ListView.White
     2: @style/Widget.ListView.White
     3: @style/Widget.ListView.White
     4: @style/Widget.ListView.White
     5: @style/Widget.ListView.White
     6: @style/Widget.ListView.White
     7: @style/Widget.ListView.White
     8: @style/Widget.ListView.White
     9: @style/Widget.ListView.White
    10: @style/Widget.ListView.White
    11: @style/Widget.Holo.Light.ListView
    12: @style/Widget.Holo.Light.ListView
    13: @style/Widget.Holo.Light.ListView
    14: @style/Widget.Holo.Light.ListView
    15: @style/Widget.Holo.Light.ListView
    16: @style/Widget.Holo.Light.ListView
    17: @style/Widget.Holo.Light.ListView
    18: @style/Widget.Holo.Light.ListView
    19: @style/Widget.Holo.Light.ListView
    20: @style/Widget.Holo.Light.ListView
    21: @style/Widget.Material.Light.ListView
    22: @style/Widget.Material.Light.ListView
    23: @style/Widget.Material.Light.ListView
    24: @style/Widget.Material.Light.ListView
    25: @style/Widget.Material.Light.ListView
    26: @style/Widget.Material.Light.ListView
    27: @style/Widget.Material.Light.ListView

# Limitations

The script has a few limitations:

1. It assumes that any resource directory which contains the path `/sdk/` is
part of the Android platform. It uses this to implicitly add the `android:`
namespace.

2. It assumes that the only platform-dependent values directory are simply
called `values-vN` where `N` is the API number. It ignored more qualified
directories like `values-fr-v21`.

3. When sweeping, it only goes up to API 27, which was the max API when
the script was written.

# License

Copyright 2018 Lawrence Kesteloot

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
