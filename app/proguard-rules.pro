# TensorFlow Lite rules
-keep class org.tensorflow.lite.** { *; }
-keep class org.tensorflow.lite.gpu.** { *; }
-keep class org.tensorflow.lite.support.** { *; }
-dontwarn org.tensorflow.lite.**

# Firebase rules
-keep class com.google.firebase.** { *; }

# Room rules
-keep class androidx.room.** { *; }

# Gson rules
-keep class com.google.gson.** { *; }

# iText rules
-keep class com.itextpdf.** { *; }
-dontwarn com.itextpdf.**

# SLF4J rules (often brought in by iText)
-dontwarn org.slf4j.**

# Support for on-device clinical AI
-keepattributes Signature
-keepattributes *Annotation*
