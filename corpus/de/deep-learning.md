---
title: Deep Learning
url: https://de.wikipedia.org/wiki/Deep_Learning
updated: '2026-08-27T01:07:18Z'
language: de
revision: '270004831'
license: CC BY-SA 4.0
source: Wikipedia
---

Deep Learning oder tiefgehendes Lernen (deutsch auch mehrschichtiges Lernen oder tiefes Lernen) bezeichnet eine Methode des maschinellen Lernens, die künstliche neuronale Netze (KNN) mit zahlreichen Zwischenschichten (englisch hidden layers) zwischen Ein- und Ausgabeschicht einsetzt und dadurch eine umfangreiche innere Struktur herausbildet. Deep Learning erlaubt die Verarbeitung und Analyse komplexer Datenmuster; dazu verwendet Deep Learning tiefe hierarchische neuronale Netze, die automatisch abstrakte Merkmale aus den Daten extrahieren. Dies ermöglicht eine effiziente Verarbeitung komplexer Informationen, was wiederum zu präzisen Vorhersagen und Entscheidungen in verschiedenen Anwendungen führt.

## Voraussetzungen und Grundlagen

Die in der Anfangszeit der künstlichen Intelligenz gelösten Probleme waren für den Menschen intellektuell schwierig, aber für Computer einfach zu verarbeiten. Diese Probleme ließen sich durch formale mathematische Regeln beschreiben.
Die wahre Herausforderung an die künstliche Intelligenz bestand jedoch in der Lösung von Aufgaben, die für die Menschen leicht durchzuführen sind, deren Lösung sich aber nur schwer durch mathematische Regeln formulieren lassen. Dies sind Aufgaben, die der Mensch intuitiv löst, wie Sprach- oder Gesichtserkennung.
Eine computerbasierte Lösung für diese Art von Aufgaben beinhaltet die Fähigkeit von Computern, aus der Erfahrung zu lernen und die Welt in Bezug auf eine Hierarchie von Konzepten zu verstehen. Hierbei ist jedes Konzept durch seine Beziehung zu einfacheren Konzepten definiert. Durch das Sammeln von Wissen aus der Erfahrung vermeidet dieser Ansatz die Notwendigkeit für die menschlichen Bediener, all das Wissen, das der Computer für seine Arbeit benötigt, formal spezifizieren zu müssen. Die Hierarchie der Konzepte erlaubt es dem Computer, komplizierte Konzepte zu erlernen, indem er sie aus einfacheren zusammensetzt. Wenn man ein Diagramm zeichnet, das zeigt, wie diese Konzepte übereinander aufgebaut werden, dann ist das Diagramm tief, mit vielen Schichten. Aus diesem Grund wird dieser Ansatz in der künstlichen Intelligenz „Deep Learning“ genannt.
Es ist schwierig für einen Computer, die Bedeutung von rohen sensorischen Eingangsdaten zu verstehen, wie in der Handschrifterkennung, wo ein Text zunächst nur als eine Sammlung von Bildpunkten existiert. Die Überführung einer Menge von Bildpunkten in eine Kette von Ziffern und Buchstaben ist sehr kompliziert. Komplexe Muster müssen aus Rohdaten extrahiert werden. Das Lernen oder Auswerten dieser Zuordnung scheint unüberwindbar schwierig, wenn sie manuell programmiert würde.
Eine der häufigsten Techniken in der künstlichen Intelligenz ist maschinelles Lernen. Maschinelles Lernen ist ein selbstadaptiver Algorithmus. Deep Learning, eine Teilmenge des maschinellen Lernens, nutzt eine Reihe hierarchischer Schichten bzw. eine Hierarchie von Konzepten, um den Prozess des maschinellen Lernens durchzuführen. Die hierbei benutzten künstlichen neuronalen Netze wurden inspiriert von Gehirnen, in denen biologische Neuronen miteinander verbunden sind.
Die erste Schicht des neuronalen Netzes, die sichtbare Eingangsschicht, verarbeitet eine Rohdateneingabe, wie beispielsweise die einzelnen Pixel eines Bildes. Die Dateneingabe enthält Variablen, die der Beobachtung zugänglich sind, daher „sichtbare Schicht“. Die erste Schicht leitet ihre Ausgaben an die nächste Schicht weiter.
Diese zweite Schicht verarbeitet die Informationen der vorherigen Schicht und gibt das Ergebnis ebenfalls weiter. Die nächste Schicht nimmt die Informationen der zweiten Schicht entgegen und verarbeitet sie weiter. Dies geht über alle Ebenen des künstlichen neuronalen Netzes so weiter.
Diese Schichten werden als versteckte Ebenen (englisch hidden layers) bezeichnet. Die in ihnen enthaltenen Merkmale werden zunehmend abstrakt. Ihre Werte sind nicht in den Ursprungsdaten angegeben. Stattdessen muss das Modell bestimmen, welche Konzepte für die Erklärung der Beziehungen in den beobachteten Daten nützlich sind. Auch die Struktur der Schichten kann je nach Modell variieren. Die Anzahl der Neuronen pro Schicht definiert die Breite des Netzes. Verschiedene Operationen wie Convolutional Filter, Addition, und Normalisierung beeinflussen die Werte in der Schicht.
Das Ergebnis wird in der letzten, wieder sichtbaren Schicht ausgegeben. Hierdurch wird die gewünschte komplizierte Datenverarbeitung in eine Reihe von verschachtelten einfachen Zuordnungen unterteilt, die jeweils durch eine andere Schicht des Modells beschrieben werden.

## Geschichte, Entwicklung und Verwendung

Die Group method of data handling-KNNs (GMDH-ANN) der 1960er-Jahre von Oleksij Iwachnenko waren die ersten Deep-Learning-Systeme des Feedforward-Multilayer-Perzeptron-Typs.
Karl Steinbuchs Lernmatrix war eines der ersten künstlichen neuronalen Netze, das aus mehreren Schichten von Lerneinheiten oder lernenden „Neuronen“ bestand. Damit war er einer der Wegbereiter des Deep Learning, bei dem es um tiefe neuronale Netze geht, die viele Aufgaben erlernen können, bei denen frühere einschichtige Perzeptronen scheitern.
Weitere Deep-Learning-Ansätze, vor allem aus dem Bereich des maschinellen Sehens, begannen mit dem Neocognitron, einer Convolutional Neural Network (CNN)-Architektur, die von Kunihiko Fukushima 1980 entwickelt wurde.
Alex Waibels CNN namens TDNN (1987) wurde durch backpropagation trainiert und erzielte Bewegungsinvarianz.
Im Jahr 1989 verwendeten Yann LeCun und Kollegen den Backpropagation-Algorithmus für das Training mehrschichtiger KNNs (siehe Multi-Layer-Perzeptron), mit dem Ziel, handgeschriebene Postleitzahlen zu erkennen.
Sven Behnke hat seit 1997 in der Neuronalen Abstraktionspyramide den vorwärtsgerichteten hierarchisch-konvolutionalen Ansatz durch seitliche und rückwärtsgerichtete Verbindungen erweitert, um so flexibel Kontext in Entscheidungen einzubeziehen und iterativ lokale Mehrdeutigkeiten aufzulösen.
Der Begriff „Deep Learning“ wurde im Kontext des maschinellen Lernens erstmals 1986 von Rina Dechter verwendet, wobei sie hiermit ein Verfahren bezeichnet, bei dem alle verwendeten Lösungen eines betrachteten Suchraums aufgezeichnet werden, die zu keiner gewünschten Lösung geführt haben. Die Analyse dieser aufgezeichneten Lösungen soll es ermöglichen, anschließende Versuche besser zu steuern und somit mögliche Sackgassen in der Lösungsfindung frühzeitig zu verhindern.
Heute wird der Begriff jedoch vorwiegend im Zusammenhang mit künstlichen neuronalen Netzen verwendet und tauchte in diesem Kontext erstmals im Jahr 2000 auf, in der Veröffentlichung Multi-Valued and Universal Binary Neurons: Theory, Learning and Applications von Igor Aizenberg und Kollegen.
Zwischen 2009 und 2012 gewannen die rekurrenten bzw. tiefen vorwärtsgerichteten neuronalen Netze der Forschungsgruppe von Jürgen Schmidhuber am Schweizer KI-Labor IDSIA eine Serie von acht internationalen Wettbewerben in den Bereichen Mustererkennung und maschinelles Lernen. Insbesondere gewannen ihre rekurrenten LSTM-Netze drei Wettbewerbe zur verbundenen Handschrifterkennung bei der 2009 Intl. Conf. on Document Analysis and Recognition (ICDAR) ohne eingebautes A-priori-Wissen über die drei verschiedenen zu lernenden Sprachen. Die LSTM-Netze erlernten gleichzeitige Segmentierung und Erkennung. Dies waren die ersten internationalen Wettbewerbe, die durch Deep Learning oder rekurrente Netze gewonnen wurden.
Die jüngsten Erfolge von Deep Learning-Methoden, wie der Gewinn eines Go-Turniers durch das Programm AlphaGo gegen die weltbesten menschlichen Spieler, gründen sich neben der gestiegenen Verarbeitungsgeschwindigkeit der Hardware auf den Einsatz von Deep Learning zum Training des in AlphaGo verwendeten neuronalen Netzes. Gleiches gilt für die seit 2020 gelungene Vorhersage von Proteinfaltungen. Diese Netze nutzen künstlich erzeugte Neuronen (Perzeptronen), um Muster zu erkennen.
Für Beiträge zu neuronalen Netzwerken und Deep Learning erhielten Yann LeCun, Yoshua Bengio und Geoffrey Hinton 2018 den Turing Award und Hinton zusammen mit John Hopfield 2024 den Physik-Nobelpreis.

## Komplexität und Grenzen der Erklärbarkeit

Tiefe neuronale Netze können eine Komplexität von bis zu hundert Millionen einzelnen Parametern und zehn Milliarden Rechenoperationen pro Eingangsdatum aufweisen. Die Interpretierbarkeit der Parameter und Erklärbarkeit des Zustandekommens der Ergebnisse ist dabei nur noch eingeschränkt möglich und erfordert den Einsatz spezieller Techniken, die unter Explainable Artificial Intelligence zusammengefasst werden.
Ein weiterer Ansatz ist die Verwendung von Methoden aus der Physik von Vielteilchensysteme (Statistische Physik).
Eine weitere Begleiterscheinung des Deep Learning ist die Anfälligkeit für Falschberechnungen, die durch geringfügig veränderte Eingabesignale ausgelöst werden können. Ein Angreifer könnte z. B. Bilddaten absichtlich so manipulieren, dass eine Bilderkennung für Bilder, die für einen Menschen normal aussehen, falsche Ergebnisse liefert. Dieses Phänomen wird unter Adversarial Examples zusammengefasst.
Zu Grenzen und Erklärbarkeit von KI gibt es zwei unterschiedliche Konzepte. Bei beiden lassen sich die Logik, die Vorhersagen und die Entscheidungen einer KI nicht einfach ausdrücken.

„Transparente KI“ unterstützt die Ausgabe von Informationen, mit denen auch komplexe Entscheidungen erklärt und für den Menschen verständlich gemacht werden können. So kann die Entscheidungsfindung überprüft und bei Bedarf korrigiert werden. Beispiele sind Entscheidungsbäume und Expertensysteme.
„Opake KI“ unterstützt keine Ausgabe von Informationen, mit denen Entscheidungen für den Menschen verständlich gemacht werden können. Beispiele sind neuronale Netze, Deep Learning und genetische Algorithmen.
Ein bekanntes Beispiel für die Risiken opaker KI ist ein Experiment, das Microsoft im Jahr 2016 mit der Veröffentlichung eines Twitter-Chatbots namens Tay durchgeführt hat. In weniger als 24 Stunden musste Microsoft den Bot abschalten, weil er damit begann, anzügliche und beleidigende Tweets zu verfassen.

## Programmbibliotheken

Neben der meist in Schulungsbeispielen zum Verständnis der internen Struktur vorgestellten Möglichkeit, ein neuronales Netz komplett eigenhändig zu programmieren, gibt es eine Reihe von Softwarebibliotheken, häufig Open Source, lauffähig auf meist mehreren Betriebssystemen, die in gängigen Programmiersprachen wie C, C++, Java oder Python geschrieben sind. Einige dieser Programmbibliotheken unterstützen GPUs oder TPUs zur Rechenbeschleunigung oder stellen Tutorials zur Benutzung dieser Bibliotheken bereit. Mit ONNX können Modelle zwischen einigen dieser Tools ausgetauscht werden.

TensorFlow (Python, JavaScript, C++, Java, Go, Swift) von Google
Keras (Python, ab Version 1.4.0 auch in der TensorFlow-API enthalten) – populäres Framework (2018) neben Tensorflow.
Caffe vom Berkeley Vision and Learning Center (BVLC)
PyTorch (Python), entwickelt vom Facebook-Forschungsteam für künstliche Intelligenz
Torch (C, Lua) (Community) und das darauf aufbauende Facebook-Framework Torchnet
Microsoft Cognitive Toolkit (C++)
PaddlePaddle (Python) vom Suchmaschinenhersteller Baidu
OpenNN (C++), implementiert ein künstliches neuronales Netz.
Theano (Python) von der Université de Montréal
Deeplearning4j (Java) von Skymind
MXNet von der Apache Software Foundation
