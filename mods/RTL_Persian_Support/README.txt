# RTL_Persian_Support — Build & Packaging Instructions

`RTL_Persian_Support` provides runtime Harmony patches for RimWorld (`1.5` & `1.6`), bundling **Vazirmatn** (`Vazirmatn.ttf`, default) and **Iranian Sans** (`IranianSans.ttf`, classic fallback), a standard `UAX #9` Unicode BiDi reorderer (`BidiReorder`), width-aware paragraph wrapping (`FixForWidth`), world-map feature shaping, and `LanguageWorker_Persian`.

## Building from Source (.NET SDK 8.0+)

### Without Local Steam Assemblies (CI / Cross-Platform)
Uses `Krafs.Rimworld.Ref` (`1.6.4871`) NuGet reference assemblies automatically when local RimWorld Managed DLLs are not found:

```bash
dotnet build mods/RTL_Persian_Support/Source/RTL_Persian_Support.csproj -c Release -p:UseLocalManaged=false
dotnet test mods/RTL_Persian_Support/Tests/RTL_Persian_Support.Tests.csproj -c Release
```

### Against Local RimWorld Installation
```bash
dotnet build mods/RTL_Persian_Support/Source/RTL_Persian_Support.csproj -c Release -p:RimWorldManagedDir="/path/to/RimWorld/RimWorldLinux_Data/Managed"
```

Or open `RimWorld-Farsi.sln` at the repository root in Visual Studio / Rider.
