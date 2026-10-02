#Requires AutoHotkey v2.0

; Runtime routing policy. TopicCatalog.md describes it; documentation is not loaded.
; LegacyIds() remains exclusively historical filename/content compatibility.
BuiltInTopics() => Map(
    "accounts", {Key: "K", Color: "F7DC6F"},
    "applications", {Key: "A", Color: "7BC96F"},
    "azure-vm", {Key: "A", Color: "0089D6"},
    "customer-communication", {Key: "", Color: "F8B195"},
    "dns", {Key: "G", Color: "4DD0E1"},
    "fortigate", {Key: "Y", Color: "EE3124"},
    "hardware", {Key: "H", Color: "FF9F43"},
    "identity", {Key: "I", Color: "B39DDB"},
    "interview-behavioral", {Key: "2", Color: "C792EA"},
    "interview-personal", {Key: "4", Color: "C792EA"},
    "interview-questions", {Key: "5", Color: "C792EA"},
    "interview-star", {Key: "3", Color: "C792EA"},
    "interview-technical", {Key: "1", Color: "C792EA"},
    "linux", {Key: "B", Color: "FCC624"},
    "macos", {Key: "U", Color: "B0BEC5"},
    "mapped-drives", {Key: "X", Color: "81D4FA"},
    "methodology", {Key: "M", Color: "6BCB77"},
    "network", {Key: "N", Color: "45B7D1"},
    "onedrive-sync", {Key: "D", Color: "0078D4"},
    "outlook", {Key: "O", Color: "2B88D8"},
    "performance", {Key: "L", Color: "FFD93D"},
    "phishing", {Key: "S", Color: "FF5A5F"},
    "placeholder-active", {Key: "", Color: "90A4AE"},
    "placeholder-archived", {Key: "", Color: "78909C"},
    "power", {Key: "H", Color: "FF9F43"},
    "printing", {Key: "R", Color: "A8DADC"},
    "prioritization", {Key: "", Color: "FFB4A2"},
    "services", {Key: "W", Color: "00A4EF"},
    "sharepoint", {Key: "S", Color: "1AA3A3"},
    "teams", {Key: "T", Color: "6264A7"},
    "ticketing", {Key: "", Color: "80CBC4"},
    "vpn", {Key: "V", Color: "26A69A"},
    "windows", {Key: "W", Color: "00A4EF"},
    "windows-365", {Key: "W", Color: "00A4EF"})

ConfiguredShortcutGroups() => Map(
    "A", ["applications", "azure-vm"],
    "S", ["sharepoint", "phishing"],
    "H", ["hardware", "power"],
    "W", ["windows-365", "services", "windows"])

DefaultShortcut(id) {
    builtIns := BuiltInTopics()
    return builtIns.Has(id) ? builtIns[id].Key : ""
}

ValidTopicShortcut(id, key) {
    builtIns := BuiltInTopics()
    if builtIns.Has(id)
        return key = builtIns[id].Key
    return RegExMatch(key, "^[A-Z]?$") && (key = "" || !InStr("CE", key))
}

; A collision is intentional only for the exact configured built-in members.
BuildShortcuts() {
    global Shortcuts, ShortcutGroups, ShortcutWarnings
    Shortcuts := Map(), ShortcutGroups := Map(), ShortcutWarnings := "", assigned := Map()
    configured := ConfiguredShortcutGroups(), reserved := Map()
    for id, policy in BuiltInTopics()
        if policy.Key != ""
            reserved[policy.Key] := id
    for collection in [Topics, Archived]
        for id, item in collection {
            key := item.Shortcut
            if key = ""
                continue
            if !assigned.Has(key)
                assigned[key] := []
            assigned[key].Push(id)
        }
    for key, members in assigned {
        if configured.Has(key) {
            legitimate := true
            for id in members {
                found := false
                for expected in configured[key]
                    if expected = id
                        found := true
                if !found
                    legitimate := false
            }
            if legitimate {
                ShortcutGroups[key] := configured[key].Clone()
                continue
            }
        } else if members.Length = 1 && (!reserved.Has(key) || reserved[key] = members[1]) {
            Shortcuts[key] := members[1]
            continue
        }
        ShortcutWarnings .= key " "
    }
}

TopicShortcutEnabled(item) {
    if Shortcuts.Has(item.Shortcut)
        return Shortcuts[item.Shortcut] = item.Id
    if ShortcutGroups.Has(item.Shortcut)
        for id in ShortcutGroups[item.Shortcut]
            if id = item.Id
                return true
    return false
}

ShortcutTarget(key) {
    items := DisplayedTopics()
    if Shortcuts.Has(key)
        return items.Has(Shortcuts[key]) ? Shortcuts[key] : ""
    if !ShortcutGroups.Has(key)
        return ""
    available := []
    for id in ShortcutGroups[key]
        if items.Has(id)
            available.Push(id)
    if !available.Length
        return ""
    for i, id in available
        if id = CurrentId
            return available[Mod(i, available.Length) + 1]
    return available[1]
}

EffectiveTopicColor(id) => TopicColors.Has(id) ? TopicColors[id] : HeadingColor
