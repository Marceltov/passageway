---
title: Selbstüberwachtes Lernen
url: https://de.wikipedia.org/wiki/Selbst%C3%BCberwachtes_Lernen
updated: '2025-01-01T17:36:20Z'
language: de
revision: '251812224'
license: CC BY-SA 4.0
source: Wikipedia
---

Selbstüberwachtes Lernen ist ein Teilgebiet des maschinellen Lernens, das eine Zwischenform von überwachtem und unüberwachtem Lernen darstellt. Es handelt sich um eine Art autonomes Lernen mit Hilfe künstlicher neuronaler Netze, bei dem keine durch Menschen im Voraus klassifizierten Beispieldaten benötigt werden. Zunächst wird das Netzwerk mit einer Voraufgabe (pretext task) konfrontiert, die vergleichsweise einfach zu lösen und auszuwerten sind, aber ein hohes Maß an semantischem Verständnis der Daten erfordert, welches wiederum für die Lösung einer anderen, nachgelagerten Aufgabe (downstream task) nützlich ist. Während der erste Schritt meist auf durch Transformationen der Ursprungsdaten generierten Pseudo-Labeln basiert, kann die eigentliche Klassifikation mit überwachtem oder unüberwachtem Lernen durchgeführt werden. Die Idee hinter der Voraufgabe ist, dass das Lösen dieser vergleichsweise einfachen Fragestellung die Gewichte des neuronalen Netzes so initialisiert, dass das Modell auch für andere Anwendungen nützlich sein kann. Selbstüberwachtes Lernen hat in den letzten Jahren vielversprechende Ergebnisse hervorgebracht und bereits praktische Anwendung in der Bild-, Video- und Audioverarbeitung gefunden und wird unter anderem von Facebook zur automatischen Spracherkennung genutzt.

## Abgrenzung zu anderen Formen des maschinellen Lernens

Selbstüberwachtes Lernen gehört insofern zu den Verfahren des überwachten Lernens, als dass es Ziel der Methode ist, aus dem Input einen klassifizierten Output zu generieren. Gleichzeitig ist aber keine explizite Verwendung von beschrifteten Input-Output-Paaren notwendig. Stattdessen werden Korrelationen, in die Daten eingebettete Metadaten oder im Input vorhandenes Domänenwissen implizit und autonom aus den Daten extrahiert. Diese aus den Daten selbst generierten Informationen werden dann zur Klassifikation verwendet.
Selbstüberwachtes Lernen ähnelt aber auch insofern dem unüberwachten Lernen, als dass es ohne explizit vorgegebene Labels in den Beispieldaten auskommt. Im Gegensatz zum unüberwachten Lernen erfolgt das eigentliche Lernen aber nicht mit Hilfe inhärenter Datenstrukturen.
Die Kombination aus überwachtem und unüberwachtem Lernen wird als semi-überwachtes Lernen bezeichnet. Hier ist lediglich ein kleiner Teil der Lerndaten bereits gelabelt. Auch hiervon unterscheidet sich selbstüberwachtes Lernen deutlich, da es ganz ohne explizite Labels auskommt.

## Anwendung

Selbstüberwachtes Lernen ist vor allem dann wesentlich effizienter als überwachtes Lernen, wenn nur wenige Beispieldaten vorliegen, mit denen gelernt werden kann.  Insofern hat die Methode das Potential, bisherige Einschränkungen des maschinellen Lernens zu überwinden und neue Anwendungsbereiche zu erschließen. Selbstüberwachtes Lernen ist vor allem für automatische Bild-, Sprach- und Videoverarbeitung geeignet. Facebook entwickelte beispielsweise mit wav2vec einen selbstüberwachten Algorithmus, um automatische Spracherkennung durchzuführen und verwendet hierfür zwei tiefe faltende neuronale Netze, die aufeinander aufbauen. Das von Google entwickelte Modell BERT (Bidirectional Encoder Representations from Transformers) wird zum Beispiel zum besseren Verständnis des Kontextes von Suchanfragen verwendet. Darüber hinaus entstand während der Forschung von OpenAI ein autoregressives Sprachmodell namens GPT-3, das in der maschinellen Sprachverarbeitung eingesetzt werden kann. Damit könne unter anderem Texte übersetzt oder Fragen beantwortet werden. Auch bestehende Methoden wie Clustering, Dimensionalitätsreduktion oder Empfehlungssystem können mittels selbstüberwachtem Lernen verbessert werden. Konkrete Anwendungsbeispiele sind autonomes Fahren, Roboterchirurgie oder monokulare Endoskopie.

## Software

Lightly – Eine Open-Source Python-Bibliothek für selbstüberwachtes Lernen mit Bildern
OpenSelfSup – Toolbox und Benchmark für selbstüberwachtes Lernen
VISSL – VISSL ist eine Bibliothek mit erweiterbaren, modularen und skalierbaren Komponenten für selbstüberwachtes Lernen mit Bildern

## Relevante Publikationen

Das Paper ‘ALBERT: A Lite BERT for Self-Supervised Learning of Language Representation’ ist das am meisten zitierte Paper über selbstüberwachtes Lernen, obwohl es eines der Neuesten ist (Stand Dezember 2020). Es wurde geschrieben von Wissenschaftlern von Google Research und dem Toyota Technological Institute in Chicago. Das Paper wurde als Konferenzpaper im Zuge der International Conference on Learning Representations (ICLR) 2020 veröffentlicht. Das Ziel des Papers ist es den Verbrauch an Arbeitsspeicher zu verringern und die Geschwindigkeit des Trainings von BERT zu erhöhen. BERT, oder ausgeschrieben Bidirectional Encoder Representations from Transformers, ist eine Technik zum Pre-Training von maschineller Sprachverarbeitung.
"Self-Supervised Learning of Audio-Visual Objects from Video" wurde von Autoren von der University of Oxford und der University of Michigan geschrieben. Einer der Autoren ist Andrew Zisserman, ein Professor an der University of Oxford, der viel zu der Forschung an selbstüberwachtem Lernen beiträgt. Innerhalb der Arbeit erläutern die Wissenschaftler eine Methode „um ein Video in eine Menge von diskreten audio-visuellen Objekten mittels selbstüberwachtem Lernen zu transformieren“
Autoren von DeepMind und der University of Oxford veröffentlichten in den Proceedings der ICCV 2017 das Paper „Multi-Task Self-Supervised Visual Learning“. Es ist ebenfalls eines der am meisten zitierten Paper über selbstüberwachtes Lernen. Im Zuge des Papers haben die Wissenschaftler Methoden erarbeitet, um mehrere Aufgaben mit selbstüberwachtem Lernen gemeinsam ausführen zu können. Das Ergebnis der Forschung war, dass das kombinieren von mehreren Aufgaben die Leistung erhöht.
