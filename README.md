# RimWorld Farsi Translation

This project is the official Farsi language pack for RimWorld, created by Ludeon Studio, with translations contributed free of charge by the community.

Because the in-game version may not always be up-to-date, players can download and install the latest translation from this repository.

🌟 **Persian README 🇮🇷 توضیحات فارسی:** [README_fa.md](https://github.com/Ludeon/RimWorld-Farsi/blob/master/README_fa.md)

---

## 🚀 **Installation Instructions**

Follow these steps to add the Persian language to your RimWorld adventure:

### **A. Automated Method in Windows (Recommended)**

1.  Copy the `AutoFaInstall.bat` file to your main game folder.
2.  Run the file to automatically download and install the latest translation.

### **B. Standard Method**

1.  Download the latest translation from the [Releases page](https://github.com/Ludeon/RimWorld-Farsi/releases).
2.  Replace the language folders for your game version in the following paths:

    *   **Core:** Copy the contents of the `Core` folder from the zip file to `<Your RimWorld Path>\Data\Core\Languages\` and rename it to `Persian`.
    *   **Royalty:** Copy the contents of the `Royalty` folder to `<Your RimWorld Path>\Data\Royalty\Languages\` and rename it to `Persian`.
    *   **Ideology:** Copy the contents of the `Ideology` folder to `<Your RimWorld Path>\Data\Ideology\Languages\` and rename it to `Persian`.
    *   **Biotech:** Copy the contents of the `Biotech` folder to `<Your RimWorld Path>\Data\Biotech\Languages\` and rename it to `Persian`.
    *   **Anomaly:** Copy the contents of the `Anomaly` folder to `<Your RimWorld Path>\Data\Anomaly\Languages\` and rename it to `Persian`.

    **Note:** If folders with the same name already exist, delete them before copying the new ones.

    *   The `Core` folder should contain four folders (`Backstories`, `DefInjected`, `Keyed`, `Strings`) and two files (`LangIcon.png`, `LanguageInfo.xml`). Ensuring this structure is correct will prevent errors.

#### **Game Installation Paths for Different Operating Systems:**

*   **Windows:** `C:\Program Files (x86)\Steam\SteamApps\common\RimWorld\`
*   **Linux:** `~/.steam/steam/steamapps/common/Rimworld`
*   **Mac:** `~/Library/Application Support/Steam/steamapps/common/RimWorld/RimWorldMac.app` (Right-click and select "Show Package Contents" to access).



### **C. Advanced Method (for Developers)**

If you have cloned this repository to your computer, you can use **Symbolic Links** to automatically keep your local translation files in sync with the latest changes.

To create a symbolic link in Windows, you can use the `mklink /D "Target Path" "Source Path"` command in the Command Prompt (in Administrator mode).

---

## ⚠️ **Important Notes**


*   **Save Game Compatibility:** This translation is compatible with your existing saves and does not require a new game.
*   **Folder Structure:** When installing manually, pay close attention to the folder structure to avoid creating extra folders.
*   **No Extra Tools Needed:** To use this translation, you only need to download and copy the files from the [Releases](https://github.com/Ludeon/RimWorld-Farsi/releases) section. No other fonts or tools are required.

---

## 🖼️ **Screenshot**

![Screenshot (43)](https://github.com/user-attachments/assets/87633f91-a012-4567-8f07-15aec21a4be2)

---

## 🤝 **Contributing to the Translation**

This is a community-driven project, and we welcome your contributions. To help improve the translation, please follow these steps:

1.  **Fork the Project:** Start by forking this repository to your own GitHub account.
2.  **Check the Issues:** Before you begin, check the [Issues page](https://github.com/Ludeon/RimWorld-Farsi/issues) to ensure no one else is already working on the same file.
3.  **Create a New Issue:** To avoid overlapping work, create a new issue to announce which part of the translation you plan to work on.
4.  **Submit a Pull Request:** Once you've made your changes, submit a pull request to have them reviewed and merged into the project.
5.  **Follow the Translation Style:** To maintain consistency, please adhere to the style and tone of the existing translations.

### **How to Translate**

The translation files in this project are in XML format. To edit them, it is recommended to use a text editor like [Visual Studio Code](https://code.visualstudio.com/).

The structure of a text to be translated is as follows:

```xml
<!-- EN: English text to be translated -->
<SomeTag>TODO</SomeTag><!-- optional_comment -->
```

*   `<!-- EN: ... -->`: This section contains the original English text and should not be changed.
*   `TODO`: You should replace `TODO` with the Farsi translation.
*   `<!-- optional_comment -->`: These comments may contain useful information.

### **RTL (Right-to-Left) Conversion Tool**

To ensure proper display of Persian text, Python-based tools are used. To contribute to the translation and build the final files, you need to fork this repository and run the Persian text correction workflow in your fork.

---

## ⭐ **Support the Project**

If you enjoy this translation and find it useful, please consider supporting us by giving this project a star on GitHub. It motivates us to continue improving and updating the translation.

---

## 📛 **Bug Reports**

If you find any errors in the translation, please create an **Issue** on the [Issues page](https://github.com/Ludeon/RimWorld-Farsi/issues) or fix it yourself and submit a pull request.

---

## ❓ **Frequently Asked Questions (FAQ)**

*   **How do I find my game installation folder?**
    *   In Steam, right-click on RimWorld, go to `Manage`, and select `Browse local files`.

*   **How do I change the language in the game?**
    *   In the main menu, click the flag icon and select your desired language.

---

## 🚫 **What Is Not Translated**

The following parts of the game remain in English due to technical limitations or to preserve authenticity:

*   Preset character names for specific factions (no official translation interface provided).
*   The development team list (to preserve the original text).
*   Some key names in the hotkey settings.
*   Content in developer mode (no official translation interface provided).


## 🏆 **Contributors and Acknowledgements**

### **Active Translator**
*   [@DanialPahlavan](https://github.com/DanialPahlavan)

### **Past Contributors**
*   [@SeyedAbdollahi](https://github.com/SeyedAbdollahi)

### **Acknowledgements**
*   **@mtimoustafa** 
* **@asidsx**

---

## 📜 **License Information**

For license details, please see the [LICENSE](https://github.com/Ludeon/RimWorld-Farsi/blob/master/LICENSE) file in this repository.
