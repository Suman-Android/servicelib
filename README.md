# Python Android Library

We have created a new project and inside this project we have created one new android library name "
pythonlibrary". This Android Library is intended for use by Android developers who want to recognize
text in images and pass the result as a input to python program.

## Getting Started

This library basically has two major components ML Kit Text Recognition and Python Plugin Chaquopy

## Introduction to ML KIT Text Recognition API

The ML Kit Text Recognition API can recognize text in any Latin-based character set. With the
Cloud-based API, you can also extract text from pictures of documents, which you can use to increase
accessibility or translate documents.

Add the dependencies for the ML Kit Android libraries to your module's app-level gradle file, which
is usually app/build.gradle:

### Initial Setup

```
implementation("com.google.mlkit:image-labeling:17.0.7")
implementation("com.google.android.gms:play-services-mlkit-text-recognition:18.0.2")
implementation("com.google.android.gms:play-services-mlkit-image-labeling:16.0.8")
```

## Introduction to Python Plugin Chaquopy

Is is a simple API for calling Python code from Java/Kotlin, and vice versa.

In your top-level build.gradle file, set the Chaquopy version:

```
plugins {
id 'com.chaquo.python' version '13.0.0' apply false
}
```

**In the module-level build.gradle file (usually in the app directory),**
apply the Chaquopy plugin after the Android plugin:

```
plugins {
id 'com.android.application'
id 'com.chaquo.python'
}
```

You can set your app’s Python version & abiFilters like this:

```
defaultConfig {
python {
buildPython "C:/path/to/python.exe"
buildPython "C:/path/to/py.exe", "-3.8"
}
ndk {
       abiFilters "armeabi-v7a", "arm64-v8a", "x86", "x86_64"
    }
}
```

## Integrating PythonLibrary with Ebol Custom Module

Firstly, You have to publish this "pythonlibrary" to LocalMaven repository. Then add this published
library as a dependency in your Ebol Custom Module.

```kotlin
    implementation("com.estes.ebol:pythonlibrary:1.0.0")
````

**Here's where the default local repository is located based on OS:
Windows: C:\Users\<User_Name>\.m2\repository 
Linux: /home/<User_Name>/.m2/repository 
Mac: /Users/<user_name>/.m2/repository**
