# RimWorld Farsi Translation – Comprehensive TODO

**Status:** Active Development
**Source:** `TranslationReport.txt` (In-game translation tool report)
**Missing Keyed Translations:** ~1,093 items
**Missing Def-Injected Translations:** ~34,379 items

---

## ⚠️ PRIORITY 1: KEYED TRANSLATIONS (UI & Gameplay)
*These files control the interface, menus, and common messages. They are critical for the game to be playable in Persian.*

### **General UI & Dialogs**
- [ ] `Dialogs_Various.xml` (Large number of missing keys)
- [ ] `Dialog_StatsReports.xml`
- [ ] `Dialog_Trees.xml`
- [ ] `FloatMenu.xml` (Right-click menu options)
- [ ] `GameplayCommands.xml` (Buttons and gizmos)
- [ ] `MainTabs.xml`
- [ ] `Menus_Main.xml`
- [ ] `Menu_Options.xml`
- [ ] `Credits.xml` (Check for argument mismatches)

### **Messages & Letters**
- [ ] `Letters.xml` (Quest notifications, threats)
- [ ] `Messages.xml` (Top-left notifications)
- [ ] `Misc_Gameplay.xml` (Huge file, contains many gameplay strings)

### **World & Scenario**
- [ ] `ScenParts.xml`
- [ ] `TerrainTags.xml`

---

## ⚠️ PRIORITY 2: DEF-INJECTED TRANSLATIONS (Content)
*These define the names and descriptions of items, backstories, animals, and quests. There is a massive amount of missing content here.*

### **Backstories (Character History)**
*There are thousands of untranslated backstories. These are low priority for mechanics but high priority for "flavor".*
- [ ] `Offworld_Medieval_Adult.xml`
- [ ] `Offworld_Nonspecific_Adult.xml` & `Child.xml`
- [ ] `Offworld_Specific_Adult.xml`
- [ ] `Solid_Adult.xml` & `Child.xml`
- [ ] `ImperialCommon_Adult.xml` & `Child.xml` (Royalty)
- [ ] `ImperialFighter_Adult.xml` & `Child.xml` (Royalty)
- [ ] `ImperialRoyal_Adult.xml` & `Child.xml` (Royalty)

### **Quests (Scripts)**
*Quest descriptions and names are largely missing.*
- [ ] `Script_TradeRequest.xml`
- [ ] `Script_TransportPodCrash.xml`
- [ ] `Script_WandererJoins.xml`
- [ ] `Scripts_Missions.xml`
- [ ] `Script_Hospitality_Refugee.xml`
- [ ] `Script_PawnLend.xml`
- [ ] `Script_RelicHunt.xml` (Ideology)
- [ ] `Script_WorkSite.xml` (Ideology)
- [ ] `Script_MechanitorShip.xml` (Biotech)
- [ ] `Script_SanguophageShip.xml` (Biotech)

### **Interactions & Tales**
*Social interactions and art descriptions.*
- [ ] `Interactions_Social.xml`
- [ ] `Interactions_Romance.xml`
- [ ] `Interactions_Prisoner.xml`
- [ ] `Interactions_Animal.xml`
- [ ] `Tales_Job.xml`
- [ ] `Tales_Incident.xml`
- [ ] `Tales_Health.xml`
- [ ] `RulePacks_Global.xml`
- [ ] `RulePacks_Namers_*.xml` (All Namer files)

### **Game Concepts & Tutorial**
- [ ] `Concepts_Entry.xml`
- [ ] `Concepts_NotedOpportunistic.xml`
- [ ] `Instructions.xml` (Tutorial steps)
- [ ] `Tutor.xml`

### **Biotech & Genetics (Expansion)**
- [ ] `GeneDefs_*.xml` (All gene files: Endogenes, Abilities, Cosmetic, Health)
- [ ] `Hediffs_Mechanitor.xml`
- [ ] `Hediffs_Mechs.xml`

### **Royalty (Expansion)**
- [ ] `RoyalPermits_Empire.xml`
- [ ] `HairsRoyal.xml`
- [ ] `Hediffs_BodyParts_*_Empire.xml`

### **Health & Body**
- [ ] `Hediffs_Global_Misc.xml`
- [ ] `Hediffs_Local_Injuries.xml`
- [ ] `BodyParts_General.xml`
- [ ] `Bodies_Animal_*.xml` (All animal body definitions)

### **World Environment**
- [ ] `Biomes_*.xml` (All biome files)
- [ ] `GameConditions_*.xml` (Events like Toxic Fallout, Eclipse)

---

## 🛠️ INSTRUCTIONS FOR TRANSLATORS

1.  **Don't assume a file is done just because it exists.**
2.  Use the **Translation Report** tool in-game (Dev Mode -> Translation -> Report) to see the specific lines missing in each file.
3.  **Prioritize `Keyed` files first**, as these appear in the UI buttons and menus.
4.  **Backstories** are the largest chunk of work; do them last or divide them among multiple translators.