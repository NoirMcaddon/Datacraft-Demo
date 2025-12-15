# Datacraft CLI (Prototype)

This repository contains an **early CLI-based prototype** of Datacraft.

Datacraft is a concept that allows **storing arbitrary data inside Minecraft map files** using controlled noise encoding.

---

## ⚠️ Important Notice

This is **NOT the full product**.

This repository exists for:

* Educational purposes
* Transparency for the community
* Demonstrating the core idea

The commercial software version includes:

* Full GUI
* Optimized encoding pipeline
* Live image/video preview directly from Minecraft
* License & anti-piracy system
* Better UX & performance

---

## 🔒 License

This project is **source-available**, not open-source.

* Viewing and running is allowed
* Modification is **NOT** allowed
* Redistribution is **NOT** allowed
* Commercial use is **NOT** allowed

See the `LICENSE` file for full terms.

---

## 🎬 Creator

**Datacraft by Mcaddon**
YouTube: [https://www.youtube.com/@Mcaddon](https://www.youtube.com/@Mcaddon)

---

## 💡 Note

If you showcase this project in any form, **proper credit is mandatory**.

---

## 🚀 How to Use (CLI)

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/noirmcaddon/datacraft-cli.git
cd datacraft-cli
```

---

### 2️⃣ Open Terminal in the Project Folder

Make sure your terminal / PowerShell is opened **inside the cloned repository folder**.

---

### 3️⃣ Encode a File into Minecraft Maps

```bash
python datacraft_demo.py encode <FileName> "C:\Users\User\AppData\Roaming\.minecraft\saves\<MinecraftWorldName>"
```

**Example:**

```bash
python datacraft_demo.py encode secret.png "C:\Users\User\AppData\Roaming\.minecraft\saves\MyWorld"
```

During encoding, the tool will print:

* Starting Map ID
* Total number of maps used

It will also create an important `Metadata.txt` file inside your world folder.(See That To Decode later)

---

### 4️⃣ Decode Maps Back into a File

```bash
python datacraft_demo.py decode "C:\Users\User\AppData\Roaming\.minecraft\saves\<MinecraftWorldName>" <StartMapID> <TotalMaps> <OutputFileName>
```

**Example:**

```bash
python datacraft_demo.py decode "C:\Users\User\AppData\Roaming\.minecraft\saves\MyWorld" 1000000 15 recovered.jpg
```

**Parameters explained:**

* `1000000` → Starting Map ID
* `15` → Total number of maps used during encoding
* `recovered.jpg` → Output file name

---

### 5️⃣ View the Data Inside Minecraft

To visually see the stored data inside Minecraft, run:

```mcfunction
/give @p filled_map[minecraft:map_id=<AnyMapIDFromThatFile>]
```

Open the map in-game to view the encoded content.

**EASY PEASY 🙂**
