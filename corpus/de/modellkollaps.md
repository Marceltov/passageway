---
title: Modellkollaps
url: https://de.wikipedia.org/wiki/Modellkollaps
updated: '2026-10-23T17:04:58Z'
language: de
revision: '271559958'
license: CC BY-SA 4.0
source: Wikipedia
---

Modellkollaps bei maschinellem Lernen, respektive künstlicher Intelligenz kann bei generativen Modellen auftreten, falls unkontrolliertes zusätzliches Training mit Resultaten anderer Modelle oder früherer Versionen desselben Modells durchgeführt wird. Solche Resultate / Ausgaben werden im Gegensatz zu noch nicht von KI-Modellen verwendeten Eingaben als synthetische Daten bezeichnet. Dadurch kann allmählich ein Modell an Leistungsfähigkeit verlieren bis hin zu seinem Kollaps. Modellkollaps kann bei verschiedenartigen Modellen auftreten. Neben LLMs wie bei GPT wurde dieses Phänomen auch beim einfachen, eindimensionalen Gauss-Modell, multidimensionalen Gauss-Modellen, linearer Regression und statistischen Sprachmodellen beobachtet.
Alternative Bezeichnungen für Modellkollaps sind algorithmische Inzucht oder katastrophales Vergessen.
Es wurden zwei Stadien der Verschlechterung unterschieden: früher Modellkollaps und später Modellkollaps. Beim frühen Modellkollaps verliert das Modell Informationen aus seltener auftretenden Randgebieten. Dieses Stadium ist weniger offensichtlich, weil die Gesamtleistung des Modells kaum beeinträchtigt wird. Beim späten Modellkollaps verliert das Modell einen signifikanten Teil seiner Leistungsfähigkeit, verwechselt Konzepte und verliert den größten Teil seiner Variabilität.

## Mechanismen

Ein experimentell durchgeführter Extremfall war ein Modellkollaps, bei welchem wiederholt Resultate/Ausgaben des Modells iterativ wieder als Lerndaten in dasselbe Modell eingespeist wurden. In diesem Extremfall spricht man von einer vollsynthetischen Schleife. Dadurch verlor das Modell zunehmend seine Fähigkeit zur Generierung sinnvoller, differenzierter Ausgaben bis hin zur Unbrauchbarkeit.
In der realen Welt warnen Forscher und Kommentatoren, dass dieses Phänomen die zukünftige Entwicklung generativer KI grundlegend bedrohen könnte. Gefährdet sind insbesondere Modelle, welche fortlaufend neue Daten erfassen und als zusätzliche Lerndaten verwenden. Da KI-generierte Daten (synthetische Daten) im Internet geteilt werden, landen sie in zukünftigen Trainingsdatensätzen, die oft aus dem Internet zusammengestellt werden. Bei der Auswahl von Trainingsdaten werden teilweise Filter verwendet, welche Duplikate nicht berücksichtigen. Es wird auch versucht, KI-erstellte Daten zu kennzeichnen und sie bei weiteren Lernprozessen auszusortieren. Andere Forscher zeigten, dass ein Modellkollaps vermieden wird, wenn sich synthetische Daten neben bestimmten menschlich generierten Daten ansammeln, wie dies bei synthetischen Verstärkerschleifen oder frischen Datenschleifen der Fall ist. Die Forscher argumentieren, dass die Akkumulation von Daten über die Zeit eine realistischere Beschreibung der Realität sei als das jährliche Löschen aller vorhandenen Daten und dass die tatsächlichen Auswirkungen des Modellkollapses möglicherweise nicht so katastrophal sind, wie befürchtet.
