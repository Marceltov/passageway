---
title: Wissensdestillation
url: https://de.wikipedia.org/wiki/Wissensdestillation
updated: '2026-07-18T09:17:39Z'
language: de
revision: '268917400'
license: CC BY-SA 4.0
source: Wikipedia
---

Wissensdestillation oder Modelldestillation ist im Zusammenhang mit künstlicher Intelligenz (KI)
der Vorgang, bei dem Wissen von einem großen vortrainierten Modell durch Nachahmung auf ein kleineres übertragen wird. Während große Modelle (wie tiefe neuronale Netze oder Kombinationen mehrerer Modelle) eine größere Wissenskapazität haben als kleine Modelle, wird diese Kapazität möglicherweise nicht vollständig genutzt. Wissensdestillation überträgt Wissen von einem großen Modell (oft Lehrermodell genannt) auf ein kleineres (oft Schülermodell genannt), ohne wesentlich an Aussagekraft einzubüßen. Da kleinere Modelle mit weniger Parametern weniger teuer zu trainieren und zu nutzen sind, können sie auf weniger leistungsfähiger Hardware (wie Mobiltelefonen) eingesetzt werden. Schülermodelle dieser Art liefern rascher Resultate (Inferenzen) als die entsprechend komplexeren Lehrermodelle.
Modelldestillation ist nicht zu verwechseln mit bestimmten Arten von Modellkompression, die Methoden beschreiben, um die Größe eines großen Modells selbst zu verringern, ohne ein neues Modell zu trainieren. Modellkompression bewahrt im Allgemeinen die Modellstruktur und die nominale Anzahl der Parameter des Modells, während die Bits-pro-Parameter reduziert werden.

## Geschichte

Ein frühes Beispiel für die Destillation neuronaler Netze wurde 1991 von Jürgen Schmidhuber im Bereich der rekurrenten neuronalen Netze (RNNs) veröffentlicht. Das Problem war die Sequenzvorhersage für lange Sequenzen. Es wurde durch zwei RNNs gelöst. Einer von ihnen (der Automatisierer) sagte die Sequenz voraus, und ein anderer (der Chunker) sagte die Fehler des Automatisierers voraus. Gleichzeitig sagte der Automatisierer die internen Zustände des Chunkers voraus. Nachdem der Automatisierer die internen Zustände des Chunkers gut voraussagen konnte, begann er, die Fehler zu beheben, und bald war der Chunker überflüssig, so dass am Ende nur noch ein RNN übrig blieb.
1992 wurden Arbeiten zur statistischen Mechanik von Lehrer-Schüler-Konfigurationen veröffentlicht.
Die Komprimierung des Wissens mehrerer Modelle (einem Ensemble) in ein einziges neuronales Netz wurde 2006 als eine Art von Modellkompression bezeichnet. Die Komprimierung wurde erreicht, indem ein kleineres Modell mit großen Mengen an Pseudo-Daten trainiert wurde, die von einem leistungsstärkeren Ensemble bereits verarbeitet waren mit dem Ziel, das Logit des komprimierten Modells an das Logit des Ensembles anzupassen.
Geoffrey Hinton und seine Mitautoren formulierten 2015 das Konzept der Modelldestillation und zeigten Ergebnisse, die bei Bildklassifikation erzielt wurden.

## Methoden

Wenn Lehrer- und Schülermodell mit denselben Daten trainiert werden, hat das kleinere Modell möglicherweise nicht genügend Kapazität, um verglichen mit dem großen Modell eine prägnante Wissensdarstellung zu lernen. Es gibt jedoch Informationen über eine prägnante Wissensdarstellung, die in Pseudo-Wahrscheinlichkeiten kodiert und mit den Ausgaben (Inferenzen) verknüpft sind. Wenn ein Modell eine Klasse korrekt vorhersagt, weist es der entsprechenden Ausgabevariablen einen hohen Wahrscheinlichkeitswert zu und den anderen Ausgabevariablen kleinere Werte. Die Verteilung der Werte unter den Ausgaben für einen Datensatz liefert Informationen darüber, wie das große Modell Wissen darstellt. Indem nur das große Modell auf den Daten trainiert und seine bessere Fähigkeit zur prägnanten Wissensdarstellung genutzt wird, kann dieses Wissen in das kleinere Modell destilliert werden. Dies geschieht durch entsprechendes Training, um die Wahrscheinlichkeitsverteilung der Ausgaben des großen Modells zu lernen.
Mehrere Algorithmen werden für die Wissensdestillation verwendet, jeder mit seinem eigenen Ansatz zur Übertragung von Wissen von einem größeren Lehrermodell auf ein kleineres Schülermodell. Hier sind einige der Bemerkenswertesten:

Soft Target Distillation Dies ist der häufigste Ansatz, bei dem das Schülermodell trainiert wird, die Wahrscheinlichkeitsverteilungen (Logits) des Lehrermodells nachzuahmen. Die weichen Wahrscheinlichkeiten enthalten mehr Informationen als harte Inferenzen und helfen dem Schülermodell, besser zu lernen.
Adversarial Distillation Bei dieser Methode wird ein gegnerisches Netzwerk verwendet, um sicherzustellen, dass die Ausgaben des Schülermodells nicht von den Ausgaben des Lehrermodells zu unterscheiden sind. Dies hilft, das Wissen effektiver zu übertragen.
Multi-Teacher Distillation Dieser Ansatz beinhaltet die Verwendung mehrerer Lehrermodelle, um ein einzelnes Schülermodell zu trainieren. Das Schülermodell lernt aus dem kombinierten Wissen aller Lehrermodelle (Ensemble), was zu einer verbesserten Leistung führen kann.
Cross-Modal Distillation Diese Technik wird verwendet, wenn das Lehrer- und das Schülermodell in verschiedenen Modalitäten arbeiten (z. B. ein Modell verarbeitet Bilder, während das andere Text verarbeitet). Das Schülermodell lernt, die Ausgaben des Lehrermodells nachzuahmen, auch wenn sie in verschiedenen Formaten vorliegen.
Self-Distillation Bei dieser Methode wird dasselbe Modell sowohl als Lehrer als auch als Schüler verwendet. Das Modell wird iterativ trainiert, wobei jede Iteration die vorherige Version von sich selbst als Lehrer verwendet.
Diese Algorithmen helfen, kleinere und effizientere Modelle zu erstellen, die einen Großteil der Leistung ihrer größeren Gegenstücke beibehalten und somit für den Einsatz in ressourcenbeschränkten Umgebungen geeignet sind.

## Anwendungen

Wissensdestillation wurde erfolgreich in mehreren Anwendungen der künstlichen Intelligenz eingesetzt, wie Objekterkennung und Verarbeitung natürlicher Sprache. Bei Large Language Models (LLMs) ist Modelldestillation besonders bedeutend, weil es sich um sehr umfangreiche, komplexe Modelle mit Millionen bis Milliarden von Parametern handelt. So wurde beispielsweise das Modell DeepSeek-R1 als LLM mit 670 Milliarden Parameter auf ein daraus destilliertes Modell mit nur noch 7 Milliarden Parameter reduziert.

## Urheberrecht

Open-Source-Modelle stehen allgemein nach Lizenznahme kostenlos zur Verfügung, um das entsprechende Modell weiterzuentwickeln und auch Destillate davon anzufertigen. Bei Modellen mit Urheberschutz (proprietäre Modelle) ist jedoch das Anfertigen von Destillaten ohne Lizenznahme nicht erlaubt.
OpenAI wirft DeepSeek vor, ihre Modelle unrechtmäßig genutzt zu haben. Insbesondere sei vermutlich Wissensdestillation vorgenommen worden, um bezüglich Trainingsaufwand zu sparen und Modelle rascher zu verwirklichen. Zitat der Sprecherin von OpenAI, Liz Bourgeois: „We know that groups in the P.R.C. are actively working to use methods, including what’s known as distillation, to replicate advanced U.S. A.I. models.“
Anthropic beschuldigen Moonshot AI und andere chinesische Firmen, amerikanische Spitzentechnologie illegal angezapft zu haben. Dazu seien Tausende betrügerische Konten eingesetzt worden, um Millionen von Konversationen mit Claude zu generieren und damit eigene große Sprachmodelle zu trainieren.
