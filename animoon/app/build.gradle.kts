import java.util.Properties

// Leemos el local.properties para obtener la IP sin subirla a Git (sobrescribe el default)
val localProperties = Properties()
val localPropertiesFile = rootProject.file("local.properties")
if (localPropertiesFile.exists()) {
    localProperties.load(localPropertiesFile.inputStream())
}
// Por defecto apuntamos al emulador local
val apiBaseUrl = localProperties.getProperty("API_BASE_URL") ?: "http://10.0.2.2:8000/"

plugins {
    alias(libs.plugins.android.application)
}

android {
    namespace = "com.example.animoon"
    compileSdk {
        version = release(37)
    }

    buildFeatures {
        buildConfig = true
    }

    defaultConfig {
        applicationId = "com.example.animoon"
        minSdk = 26
        targetSdk = 36
        versionCode = 1
        versionName = "1.0"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
        
        // Inyecta la variable en la clase BuildConfig
        buildConfigField("String", "API_BASE_URL", "\"http://192.168.0.104:8000/\"")
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_11
        targetCompatibility = JavaVersion.VERSION_11
    }
}

dependencies {
    implementation(libs.androidx.activity.ktx)
    implementation(libs.androidx.appcompat)
    implementation(libs.androidx.constraintlayout)
    implementation(libs.androidx.core.ktx)
    implementation(libs.material)
    
    // Retrofit & OkHttp
    implementation(libs.retrofit)
    implementation(libs.retrofit.converter.gson)
    implementation(libs.okhttp)
    implementation(libs.okhttp.logging)

    testImplementation(libs.junit)
    androidTestImplementation(libs.androidx.espresso.core)
    androidTestImplementation(libs.androidx.junit)
}