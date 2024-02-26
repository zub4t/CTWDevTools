

/*
*  EXMAPLE OF THE MOST BASIC POSSIBLE EDITOR
*
*/

plugins {
    `java-library`
    id("application")
    alias(libs.plugins.shadow)
}

dependencies {
    implementation(libs.edc.boot)
    implementation(libs.edc.connector.core)
}

application {
    mainClass.set("org.eclipse.edc.boot.system.runtime.BaseRuntime")
}

tasks.withType {
    mergeServiceFiles()
    archiveFileName.set("basic-connector.jar")
}
    
    
    