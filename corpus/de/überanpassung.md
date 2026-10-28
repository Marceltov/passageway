---
title: Überanpassung
url: https://de.wikipedia.org/wiki/%C3%9Cberanpassung
updated: '2023-12-21T10:28:39Z'
language: de
revision: '240398362'
license: CC BY-SA 4.0
source: Wikipedia
---

Überanpassung (englisch overfitting) bezeichnet eine bestimmte Korrektur eines Modells an einen vorgegebenen Datensatz. In der Statistik bedeutet Überanpassung die Spezifizierung eines Modells, das zu viele erklärende Variablen enthält. Werden dagegen relevante Variablen außer Acht gelassen (siehe Verzerrung durch ausgelassene Variablen), spricht man von Unteranpassung (englisch underfitting).

## Mathematische Definition

Gegeben sei ein Hypothesenraum 
$H$

 und eine Hypothese 
$h\in H$

. Dann wird 
$h$

 überangepasst an die Trainingsdaten genannt, wenn es eine alternative Hypothese 
$h'\in H$

 gibt, sodass 
$h$

 einen kleineren Fehler gegenüber 
$h'$

 auf den Trainingsdaten aufweist, aber 
$h'$

 einen kleineren Fehler als 
$h$

 in Bezug auf die Verteilung aller Instanzen hat.
Eine einfache Überprüfung auf Überanpassung kann die Holdout-Methode liefern.

## Statistik

In der multiplen linearen Regression wird mit Überanpassung ein Modell charakterisiert, das zusätzliche, irrelevante Regressoren (irrelevante erklärende Variablen) enthält. Analog dazu fehlen bei einem unterangepassten Modell einige (oder sogar alle) der relevanten Regressoren.
Durch die Aufnahme zusätzlicher Regressoren kann das Bestimmtheitsmaß 
${\mathit {R}}^{2}$

, das die Güte der Anpassung des Modells an die Daten der Stichprobe misst, nicht sinken (siehe Bestimmtheitsmaß#Das adjustierte Bestimmtheitsmaß). Durch Zufallseffekte können so irrelevante Regressoren zur Erklärung der Varianz beitragen und das Bestimmtheitsmaß künstlich erhöhen.
Überanpassung ist als negativ zu beurteilen, weil also die tatsächliche (geringere) Anpassungsgüte verschleiert wird und das Modell zwar besser auf die Daten der Stichprobe angepasst wird, allerdings aufgrund fehlender Generalität keine Übertragbarkeit auf die Grundgesamtheit besteht. Regressionskoeffizienten erscheinen fälschlicherweise als nicht signifikant, da ihre Wirkung nicht mehr hinreichend genau geschätzt werden kann. Die Schätzer sind ineffizient, d. h. ihre Varianz ist nicht mehr minimal. Gleichzeitig wächst die Gefahr, dass irrelevante Variablen aufgrund von Zufallseffekten als statistisch signifikant erscheinen. Überanpassung verschlechtert so die Schätzeigenschaften des Modells, insbesondere auch dadurch, dass eine zunehmende Anzahl von Regressoren die Anzahl der Freiheitsgrade verringert. Große Unterschiede zwischen dem unkorrigierten und dem korrigierten Bestimmtheitsmaß deuten auf Überanpassung hin. Überanpassung kann vor allem durch sachlogische Überlegungen und durch Anwendung einer Faktorenanalyse entgegengewirkt werden.

## Datensätze und überangepasste Modelle

Zunächst ist die Auswahl des Datensatzes, insbesondere die Zahl von Beobachtungen, Messpunkten oder Stichproben, ein wesentliches Kriterium für eine seriöse und erfolgreiche Modellbildung. Sonst erlauben die aus diesen Daten gewonnenen Annahmen überhaupt keine Rückschlüsse auf die Wirklichkeit. Dies gilt auch insbesondere für statistische Aussagen.
Die maximal mögliche Komplexität des Modells (ohne überanzupassen), ist proportional zur Repräsentativität der Trainingsmenge und somit auch zu deren Größe bei gegebenem Signal-Rausch-Verhältnis. Hieraus entsteht ebenfalls eine Interdependenz zur Verzerrung in endlichen Stichproben (englisch finite sample bias), so dass eine möglichst abdeckende und umfangreiche Trainingsdatensammlung anzustreben ist.
Anders ausgedrückt: Wer versucht, in vorhandenen Daten nach Regeln oder Trends zu suchen, der muss geeignete Daten wählen. Wer eine Aussage über die häufigsten Buchstaben des deutschen Alphabets treffen möchte, sollte dafür nicht nur einen einzelnen Satz betrachten, zumal wenn in diesem der Buchstabe „E“ selten vorkommt.

## Überanpassung durch zu hohe Modellkapazität

Bei der rechnergestützten Modellbildung kommt ein zweiter Effekt hinzu. Hier wird in mehreren Trainingsschritten ein Datenmodell an vorhandene Trainingsdaten angepasst. Beispielsweise kann mit einigen Dutzend Schriftproben ein Rechner trainiert werden, dass er handgeschriebene Ziffern (0–9) richtig erkennt und zuordnet. Das Ziel ist hierbei, auch Handschriften von Personen erkennen zu können, deren Handschrift gar nicht in dem Trainingssatz enthalten war.
Folgende Erfahrung wird häufig gemacht: Die Erkennungsleistung für geschriebene Ziffern (unbekannter Personen) mit zunehmender Anzahl der Trainingsschritte nimmt zunächst zu. Nach einer Sättigungsphase nimmt sie aber wieder ab, weil sich die Datenrepräsentation des Rechners zu sehr an die Schreibweise der Trainingsdaten anpasst und nicht mehr an den zugrundeliegenden Formen der zu lernenden Ziffern selbst orientiert. Dieser Prozess hat den Begriff Überanpassung im Kern geprägt, auch wenn der Zustand der Überangepasstheit wie oben beschrieben eine Reihe von Gründen haben kann.
Wenn mit dem Modell kein Einsatz über die Trainingsmenge hinaus geplant ist, wenn also nur ein Modell für eine abgeschlossene Problemstellung gelöst wird, kann natürlich von Überanpassung nicht die Rede sein.
Ein Beispiel hierfür wäre, wenn nur ein Rechnermodell für die abgeschlossene Menge von Vorfahrtsituationen im Straßenverkehr gesucht wird. Solche Modelle sind deutlich weniger komplex als das oben genannte und meistens kennt man die Regeln schon, so dass von Menschen verfasste Programme hier meist effizienter sind als maschinelles Lernen.
Mit anderen Worten, das Modell merkt sich viele Beispiele, anstatt zu lernen, Merkmale zu bemerken.

## Kognitive Analogie

Ein überangepasstes Modell mag zwar die Trainingsdaten korrekt wiedergeben, da es sie sozusagen „auswendig gelernt“ hat. Eine Generalisierungsleistung, was einer intelligenten Klassifikation gleichkommt, ist allerdings nicht mehr möglich. Das „Gedächtnis“ des Modells ist zu groß, so dass keine Regeln gelernt werden müssen.

## Strategien zur Vermeidung von Überanpassung

Wie bereits erwähnt, ist es günstig bei parametrischen Modellen eine möglichst geringe Anzahl an Parametern anzustreben. Bei nichtparametrischen Verfahren ist es analog ratsam die Anzahl der Freiheitsgrade ebenso von vornherein einzuschränken. Auf ein mehrlagiges Perzeptron würde das zum Beispiel eine Beschränkung in der Größe der verdeckten Neuronenschichten (englisch hidden layers) bedeuten. 
Eine Verringerung der Anzahl der notwendigen Parameter/Freiheitsgrade kann in komplexen Fällen auch dadurch ermöglicht werden, dass vor dem eigentlichen Klassifikations-/Regressionsschritt eine Transformation der Daten durchgeführt wird. Insbesondere wären hier Verfahren zur Dimensionsreduktion unter Umständen sinnvoll (Hauptkomponentenanalyse, Unabhängigkeitsanalyse oder Ähnliche).
Von der Trainingsdauer abhängige Überanpassung im Maschinellen Lernen kann auch durch Early Stopping verhindert werden. Zur Erkennung werden Datensätze häufig nicht nur 2-fach aufgeteilt und einer Trainings- und Validierungsmenge zugeordnet, sondern es kann zum Beispiel eine 3-fache Aufteilung erfolgen. Wobei die Mengen respektive und exklusiv zum Training, zur „Echtzeitkontrolle“ des Out-Of-Sample-Fehlers (und gegebenenfalls Trainingsabbruch bei Anstieg) und zur endgültigen Bestimmung der Testgüte verwandt werden.

Regularisierung kann zur Vermeidung von Überanpassung verwendet werden, siehe Shrinkage-Schätzer.
