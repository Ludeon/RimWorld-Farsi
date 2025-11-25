# Persian RTL Support Mod Compilation Instructions

## To Fix the Errors:

1. **Remove the current DLL:**
   - Delete `mods/RTL_Persian_Support/Assemblies/RTL_Persian_Support.dll`

2. **Ensure Harmony DLL is present:**
   - Download 0Harmony.dll from Harmony mod (steam://url/CommunityFilePage/2009463077)
   - Place it in `mods/RTL_Persian_Support/Assemblies/`

3. **Create AssetBundle with Unity:**
   - Install Unity Editor (version 2019.4 or higher)
   - Create a new 2D project
   - Import IranianSans.ttf into the Assets folder
   - Select the font file in Inspector, set AssetBundle name to "persianfont"
   - Build the AssetBundle (BuildPipeline.BuildAssetBundles)
   - Copy the resulting "persianfont" file to `mods/RTL_Persian_Support/Resources/persianfont`

4. **Compile the new C# code:**
   - Use Visual Studio with RimWorld assemblies referenced
   - Compile `mods/RTL_Persian_Support/Source/RTL_Support.cs`
   - Output to `RTL_Persian_Support.dll` in Assemblies/

5. **Test:**
   - Start RimWorld in Persian language
   - Check that UI is right-aligned and Iranian Sans font is used

The new code handles RTL properly with dynamic font loading and GUI alignment.
