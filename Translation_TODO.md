# RimWorld Persian Translation TODO

**Last Updated:** 2025-11-23  
**Translation Report Summary:**
- **Missing Keyed Translations:** 1,112 entries
- **Missing Def-Injected Translations:** 24,180 entries
- **Translation Load Errors:** 44 errors (mostly type mismatches in quest scripts)

---

## 🔴 CRITICAL FIXES REQUIRED

### Translation Load Errors (44 errors)

These files contain **type mismatch errors** that prevent translations from loading correctly. The issue is translating `List<String>` fields as `String`:

#### Quest Script Files (Need Structure Fix):
- `Script_CreepjoinerJoins.xml` - questNameRules, questDescriptionRules, questContentRules
- `Script_DistressCall.xml` - questNameRules, questDescriptionRules, questContentRules
- `Script_EndGame_VoidAwakening.xml` - questNameRules, questDescriptionRules, questContentRules
- `Script_MonolithMigration.xml` - questNameRules, questDescriptionRules, questContentRules
- `Script_MysteriousCargo.xml` - questNameRules, questDescriptionRules, questContentRules
- `Script_SightstealerArrival.xml` - questNameRules, questDescriptionRules, questContentRules
- `Script_TransportPodCrash_Ghoul.xml` - questNameRules
- `Script_UnnaturalDarkness.xml` - questNameRules, questDescriptionRules, questContentRules

#### Research Projects (Need Structure Fix):
- `ResearchProjects_Anomaly.xml` - generalRules.rulesStrings for multiple research projects

#### Abilities:
- `Abilities.xml` - Missing def: SpikeLaunch_Gorehulk.description

---

## 🟡 HIGH PRIORITY - Keyed Translations (UI & Gameplay)

### Missing Keyed Translations by File (1,112 total):

| Count | File | Priority |
|-------|------|----------|
| 923 | `Misc_Gameplay.xml` | 🔴 CRITICAL |
| 44 | `GameplayCommands.xml` | 🔴 HIGH |
| 22 | `ScenParts.xml` | 🟡 MEDIUM |
| 14 | `FloatMenu.xml` | 🔴 HIGH |

| 13 | `Dialog_StatsReports.xml` | 🟡 MEDIUM |
| 13 | `Dialogs_Various.xml` | 🟡 MEDIUM |
| 12 | `Letters.xml` | 🔴 HIGH |
| 10 | `TerrainTags.xml` | 🟢 LOW |
| 6 | `Menu_Options.xml` | 🟡 MEDIUM |
| 3 | `Dialog_Trees.xml` | 🟢 LOW |
| 3 | `Messages.xml` | 🔴 HIGH |
| 3 | `MainTabs.xml` | 🟡 MEDIUM |

**Note:** Files marked as "English file" need to be created in Persian language folder.

---

## 🟢 MEDIUM PRIORITY - Def-Injected Translations

### Top Missing Def-Injected Files (24,180 total):

#### RulePacks & Narrative (High Impact on Gameplay):
| Count | File | Category |
|-------|------|----------|
| 1,461 | `RulePacks_Book_Descriptions.xml` | Book Content |
| 490 | `Interactions_Social.xml` | Social Interactions |
| 458 | `RulePacks_Book_Namers.xml` | Book Names |
| 437 | `RulePacks_Maps.xml` | Map Generation |
| 284 | `RulePacks_Namers_WorldFeatures.xml` | World Features |
| 271 | `RulePacks_Namers_Factions.xml` | Faction Names |
| 235 | `RulePacks_Art_Statues.xml` | Art Descriptions |
| 203 | `RulePacks_Namers_Faction.xml` | Faction Naming |
| 202 | `RulePacks_CombatRanged.xml` | Combat Text |
| 197 | `RulePacks_Maneuvers.xml` | Combat Maneuvers |
| 195 | `RulePacks_Namers_Landmarks.xml` | Landmark Names |
| 186 | `RulePacks_Namers_Books.xml` | Book Naming |
| 175 | `RulePacks_Namers_Xenohumans.xml` | Xenohuman Names |
| 162 | `RulePacks_GrowthMoments.xml` | Growth Events |
| 141 | `RulePacks_Art_DescriptionsPhysical.xml` | Art Descriptions |
| 131 | `RulePacks_CombatIncludes.xml` | Combat Includes |

#### Tales & Events:
| Count | File | Category |
|-------|------|----------|
| 446 | `Tales_Incident.xml` | Incident Tales |
| 369 | `Tales_Health.xml` | Health Tales |
| 298 | `Tales_Job.xml` | Job Tales |
| 286 | `Tales_SinglePawn.xml` | Single Pawn Tales |
| 230 | `Tales_DoublePawn.xml` | Double Pawn Tales |
| 98 | `Tales_Caravan.xml` | Caravan Tales |

#### Genes & Biology:
| Count | File | Category |
|-------|------|----------|
| 303 | `GeneDefs_Spectrum.xml` | Gene Spectrum |
| 245 | `GeneDefs_Endogenes.xml` | Endogenes |
| 163 | `GeneDefs_Cosmetic.xml` | Cosmetic Genes |
| 102 | `GeneDefs_Misc.xml` | Misc Genes |

#### Research:
| Count | File | Category |
|-------|------|----------|
| 236 | `ResearchProjects_Anomaly.xml` | Anomaly Research |
| 201 | `ResearchProjects_2_Electricity.xml` | Electricity Research |
| 154 | `ResearchProjects_1.xml` | Basic Research |
| 145 | `ResearchProjects_Misc.xml` | Misc Research |

#### Items & Buildings:
| Count | File | Category |
|-------|------|----------|
| 381 | `WorkGivers.xml` | Work Tasks |
| 253 | `WeaponTraitDefs.xml` | Weapon Traits |
| 216 | `Bodies_Animal_Quadruped.xml` | Animal Bodies |
| 186 | `Races_Animal.xml` | Animal Races |
| 178 | `Hediffs_BodyParts_Bionic_Empire.xml` | Bionic Parts |
| 176 | `Skills.xml` | Skills |
| 160 | `Buildings_Misc.xml` | Misc Buildings |
| 140 | `Weapons_Unique.xml` | Unique Weapons |
| 127 | `Mote_Visual.xml` | Visual Effects |
| 127 | `Hediffs_Local_Injuries.xml` | Local Injuries |
| 141 | `Hediffs_Global_Misc.xml` | Global Hediffs |
| 116 | `Buildings_Ancient.xml` | Ancient Buildings |

#### Thoughts & Needs:
| Count | File | Category |
|-------|------|----------|
| 153 | `Thoughts_Memory_Misc.xml` | Memory Thoughts |
| 143 | `Thoughts_Situation_Special.xml` | Special Situations |
| 118 | `Thoughts_Situation_Needs.xml` | Need Thoughts |

#### Stats:
| Count | File | Category |
|-------|------|----------|
| 123 | `Stats_Pawns_General.xml` | General Stats |

#### Jobs:
| Count | File | Category |
|-------|------|----------|
| 132 | `Jobs_Misc.xml` | Misc Jobs |

#### Quests:
| Count | File | Category |
|-------|------|----------|
| 186 | `Script_SpaceSites.xml` | Space Sites |
| 156 | `Script_Hospitality_Refugee.xml` | Refugee Quests |
| 117 | `Script_AncientStructures.xml` | Ancient Structures |

---

## ✅ COMPLETED TRANSLATIONS

### Backstories:
- ✅ `ImperialRoyal_Child.xml`, `ImperialRoyal_Adult.xml`
- ✅ `ImperialFighter_Child.xml`, `ImperialFighter_Adult.xml`
- ✅ `ImperialCommon_Child.xml`, `ImperialCommon_Adult.xml`
- ✅ `Solid_Adult.xml`, `Solid_Child.xml`
- ✅ `Offworld_Medieval_Adult.xml`, `Offworld_Medieval_Child.xml`
- ✅ `Offworld_Nonspecific_Adult.xml`, `Offworld_Nonspecific_Child.xml`
- ✅ `Offworld_Specific_Adult.xml`

### Factions:
- ✅ `Factions_Hidden.xml` (Ancients, Insects, Mechanoids)
- ✅ `Factions_Misc.xml` (Outlanders, Pirates, Tribes)
- ✅ `Factions_Player.xml` (Player factions)
- ✅ `Faction_Empire.xml` (Shattered Empire)

### PawnKinds:
- ✅ `PawnKinds_Empire.xml` (All imperial ranks)
- ✅ `PawnKinds_Refugee.xml`

### Biomes (Odyssey):
- ✅ `GlacialPlain.xml`
- ✅ `Glowforest.xml`
- ✅ `Grasslands.xml`
- ✅ `LavaField.xml`
- ✅ `Scarlands.xml`
- ✅ `Space.xml`

---

## 📋 TRANSLATION WORKFLOW

### Priority Order:
1. **Fix Critical Errors** - Quest scripts and research projects with type mismatches
2. **Keyed Translations** - UI elements that players see constantly
3. **High-Impact Def-Injected** - RulePacks, Tales, Interactions
4. **Content Def-Injected** - Genes, Research, Items, Buildings
5. **Polish** - Remaining files and edge cases

### Notes:
- All "placeholder exists" files need actual Persian translations to replace placeholders
- Files marked as "English file" need to be created in the Persian language directory
- Maintain XML structure and preserve all special tokens like `{0}`, `{1}`, `[PAWN_nameDef]`, etc.
- Use consistent terminology across all translations

---

**Total Progress:**
- Completed: ~200 backstory entries, 4 faction files, 2 pawnkind files, 6 biome files
- Remaining: ~25,000 translation entries across all categories