---
title: Large Language Model
url: https://de.wikipedia.org/wiki/Large_Language_Model
updated: '2026-10-22T15:48:42Z'
language: de
revision: '271533446'
license: CC BY-SA 4.0
source: Wikipedia
---

Ein Large Language Model (kurz LLM, englisch), übertragen großes Sprachmodell, ist die softwaretechnische Realisierung eines mathematischen Sprachmodells, das sich durch seine Fähigkeit zur Textgenerierung auszeichnet. Es handelt sich um ein sogenanntes computerlinguistisches Wahrscheinlichkeitsmodell, das statistische Wort- und Satzfolge-Beziehungen aus einer Vielzahl von Textdokumenten durch einen rechenintensiven Trainingsprozess erlernt hat und diese Fähigkeiten seinem Benutzer oder einer anderen Anwendung zur Verfügung stellt.
Bei LLMs handelt es sich dabei um eine Reihe von Techniken (Algorithmen) und anderen Softwareartefakten (Frameworks und Programmbibliotheken) im Bereich moderner künstlicher Intelligenz (KI), die seit etwa Mitte der 2010er Jahre existieren und seit den 2020er Jahren vermehrt auf der Basis des Cloud Computing bereitgestellt werden. Dabei kommen Serversysteme mit KI-optimierten Mikrochips zum Einsatz. Einige Softwareanwendungen erlauben die lokale Ausführung von LLMs, welche jedoch durch die Anforderungen an die Computerhardware begrenzt sind. Der Trainingsprozess der Modelle lässt sich dabei grob in drei Phasen unterteilen: 1. Datenerfassung, 2. Modelltraining und 3. Feinabstimmung. Anschließend wird das trainierte Modell mittels Inferenz abgefragt. Häufig werden vortrainierte Modelle verwendet, wie die GPT-Modelle.
LLMs sind Teil des Deep Learning (DL) oder maschinellen Lernens (ML) und zählen zu den generativen KI-Modellen (englisch Generative AI). Die Erweiterung der LLM sind die Vision Language Models (VLM), also KI-Modelle, die sowohl Sprache als auch Computer Vision kombinieren. Sie sind Teil des multimodalen Lernens. Die fortschrittlichsten Entwicklungen bei den Modellen sind bekannt als Foundation Models, also neuartige „Grundmodelle“ einer komplexeren KI-Softwarearchitektur.
LLMs sind ein prägendes Merkmal der KI-Ära.

## Beschreibung

Große Sprachmodelle erlangen ihre Fähigkeiten durch die Verwendung großer Datenmengen, um während des Trainings riesige Mengen von Parametern zu lernen. Sie sind im weiteren Sinne künstliche neuronale Netze (KNN) und werden entweder durch selbstüberwachtes Lernen (a priori) oder halbüberwachte Lernmethoden trainiert.
Für diese künstlichen neuronalen Netze werden seit etwa dem Jahr 2018 sogenannte „Transformer“-Architekturen als Kern des Modells gewählt. Bekanntheit erlangten dabei die Generative-Pretrained-Transformer-(GPT-)Modelle sowie das Modell Bidirectional Encoder Representations from Transformers (BERT). Diese Modelle sind LLMs. BERT wurde 2018 von Google veröffentlicht. Wenig später wurde „XLNet“ zur Verbesserung von BERT publiziert.
Große Sprachmodelle arbeiten als „selbstanpassende Sprachmodelle“, die „verschiedene Aufgaben in natürlicher Sprache ausführen können, z. B. das Zusammenfassen, Übersetzen, Vorhersagen und Erstellen von Texten, indem sie einen Eingabetext nehmen und wiederholt das nächste Token oder Wort vorhersagen“.
Nach Stephen Wolfram ist die Mechanik eines LLMs etwa wie folgt: „Es fügt einfach ein Wort nach dem anderen hinzu.“ Es wird ein Token hinzugefügt, das beispielsweise nur ein Wortteil sein kann. Daher kann es vorkommen, dass neue Wörter gebildet werden. Das Programm kann „Sätze“ generieren, in denen jedes Wort unabhängig und zufällig mit der gleichen Wahrscheinlichkeit ausgewählt wird, mit der es im Korpus vorkommt. Laut Wolfram ist die Grundidee, ein Modell zu entwickeln, mit dem man die Wahrscheinlichkeiten für das Auftreten von Sequenzen schätzen könne, auch wenn man diese Sequenzen im untersuchten Textkorpus nie explizit gesehen habe. Er meint, es werden einfach Dinge gesagt, die sich „richtig anhören“, basierend darauf, wie sie im Trainingsmaterial „klangen“. Laut Wolfram sei das Ganze auf einer übergeordneten Ebene noch nicht ganz klar.
Bis etwa 2020 bestand die einzige Möglichkeit, ein Modell an bestimmte Aufgaben anzupassen, in der sogenannten Feinabstimmung. Größere LLM-Modelle, wie z. B. das inzwischen populäre GPT-3, wurden jedoch so konzipiert, dass sie mit Hilfe des sogenannten „Prompt-Engineering“ ähnliche Ergebnisse erzielen können. Zusätzlich zu der Fähigkeit, Kenntnisse über Syntax, Semantik und „Ontologie“ in menschlichen Sprachkorpora zu erwerben, wird angenommen, dass große Sprachmodelle auch in der Lage sind, Ungenauigkeiten und Verzerrungen in den Korpora zu erfassen.

## Entstehung und Entwicklung

### Vorläufer

Den modernen LLMs gingen verschiedene Entwicklungsstufen voraus. Sie beruhen auf der Verarbeitung natürlicher Sprache. Dazu zählen die statistische Zerlegung eines Textes in Fragmente, auch bekannt als N-Gramm-Analyse.
Ab den 2010er Jahren haben künstliche neuronale Netzwerke diese Fähigkeiten vertieft und erweitert. Für das „generative Lernen“ bzw. unüberwachte Lernen wurden ab 2014 die Generative Adversarial Networks (GANs) vorgestellt. Die Semi-supervised Sequence Learning-Technik, ein Trainingsalgorithmus aus dem Jahr 2015, verbessert beispielsweise das Modelltraining durch die Nutzung sowohl markierter als auch unmarkierter Daten.
Im Jahr 2016 erreichte AlphaGo, ein KI-Modell von Google DeepMind, eine neue Leistungsgrenze „künstlicher Intelligenz“ gegen den Go-Spieler Lee Sedol. Es basierte u. a. auf der Technik und Algorithmik der Convolutional Neural Network (CNN) und Monte Carlo Tree Search (MCTS) und ist primär für mathematische Spiele optimiert. Letzteres Verfahren (MCTS) ist eine Verbesserung der Minimax-Methode.

### Evolution der LLMs

Diese Entwicklungen wurden wiederum durch die Inhalte der Preprint-Publikation Attention Is All You Need (Aufmerksamkeit ist alles, was du brauchst), vorgestellt auf der Conference on Neural Information Processing Systems 2017 durch ein Google-Forscherteam, entscheidend geprägt. Ein Ziel dieser Veröffentlichung war es, die sogenannte „Sequence-to-Sequence“ oder „Seq2seq“-Technik (auch bekannt als „Encoder-Decoder-Architektur“) zu verbessern. Die Veröffentlichung führte einen sogenannten  „englisch attention mechanism  ‚Aufmerksamkeitsmechanismus‘“ ein. Die Google-Arbeit stellte somit eine neue Transformer-Technik vor. Die ersten Forschungen zu diesen Algorithmen gehen jedoch bis in die 1990er Jahre unter Jürgen Schmidhuber zurück. Mit Googles Variante war ab 2017 ein neuer Stand des (bisherigen) maschinellen Lernens (ML) oder genauer Deep Learnings (DL) für die Sprachverarbeitung (LLMs) erreicht worden. Google Research verweist dabei auf die Tensor2Tensor (T2T)-Programmbibliothek (archiviert 2023), welche ML/DL verbessert und verschiedene Transformer anbietet.
Transformer ermöglichen eine genauere und umfassendere Verarbeitung und Analyse von Textinformationen. Letztere sind sequenzielle Daten, die Transformer für Aufgaben wie Spracherzeugung und Übersetzung verstehen und erzeugen können. Sie sind ein neuronales Netzwerk, das Kontext und somit Bedeutung lernt, indem es die Beziehungen zwischen den Wörtern in einem Satz analysiert.
Im Jahr 2018, kurz nach der Veröffentlichung der Transformer-Technik, wurden das Modell Bidirectional Encoder Representations from Transformers (BERT) von Google AI vorgestellt. Obwohl der ursprüngliche Transformer sowohl Encoder- als auch Decoderblöcke hat, ist BERT ein reines Encoder-Modell.
Die Entwicklungsabteilung von OpenAI arbeitete ebenfalls seit 2015 an einem neuen Modell. Das LLM-Modell GPT-1 wurde im Jahr 2018 jedoch als reines Decoder-Modell eingeführt. Die GPT- und BERT-Modelle wurden auf der Datenbasis „BookCorpus“ trainiert. Dieser Datensatz bzw. Textkorpus enthält 7.000 selbstpublizierte Bücher und etwas unter einer Milliarde Wörter. Auch Google hat 2016 eine Vielzahl an Büchern für das Training seiner LLM verwendet. Forscher aus den Bereichen Industrie und Robotik versuchen hingegen, physikalische Umgebungsdaten zu erlernen und ihre Modelle entsprechend zu trainieren, auch als „Physical AI“ bezeichnet.
Das Modell GPT-2 wurde schließlich im Frühjahr 2019 veröffentlicht. Laut OpenAI wurde zunächst ein kleineres Modell veröffentlicht, da die Entwickler sich wie folgt äußerten: „Große, allgemeine Sprachmodelle könnten bedeutende gesellschaftliche Auswirkungen haben und bieten zudem zahlreiche kurzfristige Anwendungsmöglichkeiten.“ Sie verwiesen auf eine Vielzahl möglicher böswilliger Zwecke, die mit diesen Modellen verfolgt werden können, beispielsweise Deepfakes oder irreführende Nachrichtenartikel. Die Veröffentlichung der LLMs wird teilweise von einer Richtlinie (Policy) im Sinne einer Regulierung begleitet.
GPT-2 wurde grundsätzlich so trainiert, dass es das nächste Wort in 40 GB Internettext (Daten) vorhersagen kann, d. h. wenn alle vorherigen Wörter gegeben sind. Es ist ein Sprachmodell mit 1,5 Milliarden Parametern, das mit einem Datensatz von 8 Millionen Webseiten trainiert wurde und auf Transformer-Technik basiert. Die GPT-2 Entwicklung wurde mittlerweile eingestellt und steht unter einer modifizierten MIT-Lizenz. Die Forschungsergebnisse wurden 2019 publiziert.
GPT-3 aus dem Jahr 2020 war die nächste Entwicklungsstufe. Bis zu dem Modell GPT-3.5 waren alle OpenAI GPT-Modelle nur per Programmierschnittstelle (API) zu nutzen, was sich ab Ende 2022 änderte, als die webbasierte-Schnittstelle ChatGPT veröffentlicht wurde.
2023 wurde GPT-4 für seine erhöhte Genauigkeit und als „heiliger Gral“ für seine multimodalen Fähigkeiten gepriesen. Die genaue Softwarearchitektur und weitere Details des Modells wurden jedoch nicht öffentlich bekannt gegeben.
Seit dieser Zeit haben konkurrierende Sprachmodelle hinsichtlich der Anzahl der Parameter größtenteils mit der GPT-Serie gleichgezogen. Beispielsweise übertraf im Jahr 2024 das Modell Google Gemini Pro das GPT-4, was die Elo-Bewertung betrifft. Letztere wird im Umfeld von LLM zum Benchmarking verwendet.
Das Git-Repository von BERT wurde Ende 2025 archiviert (Entwicklung eingefroren oder gestoppt). Eine Weiterentwicklung von BERT durch Facebook AI ist bekannt geworden als RoBERTa (Robustly Optimized BERT Pretraining Approach).
Die modernsten Modelle (sowohl algorithmisch, als auch softwarearchitektonisch) werden als „Frontier Modelle“ bezeichnet. Diese Modelle weisen beispielsweise eine Mixture-of-Experts (MoE)-Architektur und weitere algorithmische Bausteine einer komplexen LLM-Architektur auf. Das MoE-Konzept geht auf Arbeiten aus den 1990er Jahren zurück und fand ihre Nutzung als Teil von ML/DL.
Die Technik der Transformer ist nach wie vor Teil der Forschung (und gegebenenfalls Entwicklung).

## Umsetzungen und LLM-Hersteller

Beispiele für LLM-Software oder -Services oder -Apps sind Mistral AI, ChatGPT, Ernie Bot und Grok. Die Services sind dabei wie ein Chat aufgebaut, der mit seinem Benutzer kommuniziert, auch bekannt als Chatbot. Viele LLM-Hersteller (Unternehmen) sind Teil der modernen Digital Economy und versuchen, die LLM-Modelle zu monetarisieren. Zu den Anbietern von LLMs zählen unter anderem (Beispiele):

## LLM-Infrastruktur

### IT, Rechenzentren und Energiebedarf

Das Training von LLMs benötigt extrem viele Rechenressourcen (speziell Speicher, siehe unter Hardware). Schätzungsweise benötigte das Training des GPT-4-Modells von OpenAI rund 50 GWh Energie (Strom) und kostete etwa 100 Millionen US-Dollar. Dies entspricht dem Stromverbrauch von San Francisco über drei Tage. Für diese neuen Größenordnungen in der IT-Welt werden seit den 2020er Jahren eigens entwickelte und für KI oder LLMs optimierte Rechenzentren aufgebaut. Schon heute werden rund 4,4 Prozent des gesamten Stromverbrauchs in den USA für Rechen- oder Datenzentren aufgewendet. Schätzungen zufolge wird sich diese Zahl drastisch erhöhen. Das Lawrence Berkeley National Laboratory (LBL) schätzt, dass bis 2028 mehr als die Hälfte des Stroms in Datenzentren für KI-Modelle verwendet wird. Zu diesem Zeitpunkt könnte KI allein so viel Strom verbrauchen wie 22 % aller US-Haushalte. In den USA wurde 2025 das Stargate-Projekt angekündigt, eine Initiative für KI-optimierte Rechenzentren der Administration Trump II. Des Weiteren wurde die Pax-Silica-Initiative angekündigt, um die Lieferketten bei Halbleiterprodukten zu beeinflussen und sicherzustellen.
Im Rahmen eines Projekts untersuchen Fachleute den Stromverbrauch der LLMs und sammeln die Ergebnisse in einer Datenbank namens ML.ENERGY Benchmark. Ein weiteres Teilprojekt von ML.ENERGY namens „Zeus“ versucht, den Energieverbrauch von Deep Learning (DL)-Applikationen (Modellen) zu messen und zu optimieren.

### Hardware

Für LLMs kommen nur modernste Prozessorgenerationen bzw. spezialisierte Mehrkernprozessoren zum Einsatz. Im Speziellen sind die „KI-Beschleuniger“ gemeint. Aufgrund der parallelen Abläufe und Datenzugriffe bei Convolutional Neural Networks (CNN) haben sich Grafikprozessoren (in Form von Grafik- oder spezialisierten Prozessorkarten), die besonders gut für Fließkommaoperationen (vgl. IEEE 754) geeignet sind, als geeignet erwiesen. Um die Modelle und deren Speicheranforderungen zu optimieren („Quantisierung“), geht man von 32-, zu 16-, 8- und mittlerweile zu kleinen 4-Bit Fließkommazahlen (FP – vgl. auch Minifloat) bzw. Operationen über. Der Hintergrund ist, dass KI-Systeme für unterschiedliche Aufgaben unterschiedliche Präzisionen erfordern, die typischerweise in Bit angegeben werden. Ein kleineres Präzisionsmaß wie 8 Bit reduziert die erforderlichen Rechenleistungen. Wie bei vielen technischen Problemstellungen muss auch hier ein Kompromiss zwischen Geschwindigkeit und Genauigkeit abgewogen werden, je nach Herausforderung.
Große LLMs Modelle stellen grundlegend enorm hohe Anforderungen an die Computerressourcen, speziell den Grafikprozessor (GPU) und den Grafikspeicher (VRAM, genauer: High Bandwidth Memory (HBM)), oder an einen spezialisierten „KI-Beschleuniger“ als separate Hardwareressource. Der Speicherbedarf M in GB lässt sich grob abschätzen:

$M_{min}\approx P\times (Q/8)\times (1+O)$

Darin sind P die Anzahl der Parameter in Milliarden, Q die Präzision in Bits (Q/8 in Bytes) und O ein zusätzlicher Speicherbedarf (Overhead) für Cache usw. in %. Für das GPT-OSS-20B-Modell werden 
$M_{min}\approx 20\times (16/8)\times (1+0.2)\approx 48$

 GB benötigt, d. h., eine moderne, dafür ausgelegte Nvidia-H100-Grafikkarte kann dies erfüllen, eine „gewöhnliche“ PC-Grafikkarten mit einstelligen GB RAM (meist DDR5) jedoch nicht. Im Falle von FP8 (Präzision der Modellgewichte während der Inferenz) werden rund 24 GB benötigt. CPU/RAM-Offloading wird in der Formel nicht berücksichtigt.
Abgesehen von diesen Modellgrößenordnungen und damit Hardwareanforderungen existieren spezialisierte ML-Modelle, z. B. TinyML oder TensorFlow Lite (ab 2026: LiteRT), für Embedded Systems, bei denen Mikrocontroller zum Einsatz kommen. Mithilfe von LiteRT können vortrainierte Modelle genutzt oder Modelle konvertiert, optimiert und schließlich in KI-optimierter Hardware ausgeführt werden. Die genauen Verfahren (Frameworks, Workflows und kompatible Geräte) müssen im Einzelfall überprüft werden.
Klassische Recurrent Neural Networks (RNN) arbeiten hingegen sequenziell, sodass GPUs oder TPUs (s. u.) hier ihre hardwarearchitektonischen Fähigkeiten nicht voll ausspielen können. Neben den klassischen Grafikprozessoren, die ihren Erfolg vor allem in der Computerspieleindustrie (Computerspielebranche) haben, gibt es jedoch bereits optimierte Chiparchitekturen, die für das Training und Inferencing von großen neuronalen Netzen designed wurden.
Im Jahr 2016 wurde beispielsweise von Google die erste Version ihres Tensor Processing Unit (TPU) Systems vorgestellt. Seit den 2020er Jahren gibt es aber eine ganze Reihe von Computerherstellern mit „KI-Beschleuniger“ für die Verwendung von LLMs. So haben beispielsweise die Unternehmen Cerebras den CS-1, CS-2 und CS-3, AMD die Instinct-Serie, Intel die Gaudi-Plattform und Nvidia Hopper bzw. dessen Nachfolger Blackwell eingeführt bzw. angekündigt.

### Software

Innerhalb der LLM-Technologie werden Softwareartefakte teilweise in Backend- und Frontend-Anteile eingeteilt. Dabei kommen eine Vielzahl von Programmbibliotheken zum Einsatz, beispielsweise PyTorch (benötigt NumPy für diverse Matrizen-Operationen) oder TensorFlow. Auch hier spielt die Optimierung bzw. Auslagerung auf GPU-Ressourcen eine Rolle: PyTorch kann das CUDA- oder das Metal Performance Shaders (MPS)-Backend (bzw. die API) von Apple nutzen.

#### Pseudo-Programmaufbau (Encoder-Decoder-Architektur)

Grundlegend (vgl. das Blockschema weiter oben):

Encoder: Eingang → Aufmerksamkeit → Addieren & Normieren → Feed Forward Netz (FFN) → Addieren & Normieren
Decoder: Eingang → Maskierte Selbst-Aufmerksamkeit → Addieren & Normieren → Kreuzaufmerksamkeit → Addieren & Normieren → FFN → Addieren & Normieren → Linearisieren → Softmax

#### Pseudo-Programmaufbau (Decoder-Architektur, GPT)

Der Aufbau zur Vorhersage des nächsten Token in einer Sequenz:

(Annahme: Grundfunktionen Softmax, Matrixmultiplikation usw. verfügbar)
Modul: Selbst-Aufmerksamkeitsmodul (Implementiert den skalierten Skalarprodukt-Aufmerksamkeitsmechanismus)
Modul: Multi-Selbst-Aufmerksamkeitsmodule (Ermöglicht dem Modell, verschiedene Aspekte der Eingabe gleichzeitig zu berücksichtigen)
Modul: Feed-Forward-Netz (FFN)
Modul: Transformer Block (Kombiniert Multi-Selbst-Aufmerksamkeitsmodule (MHA) und Feed-Forward-Netz (FFN) mit Residualverbindungen)
GPT-Modell (Decoder-Transformer, der das nächste Token in einer Sequenz vorhersagt)
Initialisierung von Modellparametern
Initialisierung der Gewichte mit einer Normalverteilung
Vorwärtsdurchlauf durch das Modell (liefert die vorhergesagten Token-Logits)
Autoregressive Generierung neuer Token (Textgenerierung)

#### Rahmenprogramm

Laden und vorbereiten von Daten (Text)
Tokenisierung und Encodierung
Modell Initialisierung (siehe GPT oben)
Laden eines Optimierers zum Lernen
Trainieren des Modells (Schleife)
Speichern des Modells (Validierung, Decodierung)

### Anwendungen

LLMs werden in verschiedenen IT-Umgebungen bzw. -Systemen (vgl. Cloud) im Zuge von Onlineservices von verschiedenen Internetdienstleistern angeboten. Letztere sind meist als Startups oder Innovationsabteilungen in Organisationen oder Unternehmen aufgestellt. Dabei ist es wichtig, dass einzelne Serviceanbieter unterschiedliche Modelle (oder Kombinationen) anbieten oder in ihre Produkte integrieren, beispielsweise Copilot, dort die Modelle GPT- oder Claude.
Des Weiteren können seit den 2020er Jahren manche Modelle das Internet durchsuchen (vgl. Webcrawler) und die gefundenen Daten auswerten.
Die Lizenzen in Bezug auf die Fähigkeiten, Nutzung und Datenverarbeitung der verschiedenen Modelle und Services reichen von proprietär über Open Source bis hin zu anderen. In diesem Zusammenhang spielt auch der Datenschutz eine übergeordnete Rolle.

## Offene Modelle und Lokale LLMs

Einige Entwickler von LLMs bieten Modelle an, die als „Offene Modelle“ oder nach eigener Definition als „Open Source“ verfügbar sind. Dazu zählen beispielsweise die OpenAI-Modelle GPT-OSS mit „offenen Gewichten“. Dabei bezeichnen „Open Weights“ die finalen Gewichte und Bias-Werte eines trainierten neuronalen Netzes. Diese Modelle werden auch als „Dual-Use Foundation Models“ bezeichnet. Die Open Source Initiative (OSI) verfolgt eine eigene Definition von „offenen KI-Modellen“, die sich von der Definition der meisten Hersteller unterscheidet.

### Offene Modelle

Im Jahr 2022 veröffentlichten über 1.000 KI-Entwickler das Modell BLOOM (BigScience Large Open-science Open-access Multilingual Language Model). Es umfasst rund 176 Milliarden Parameter, also eine Milliarde mehr als das GPT-3 Modell.
Facebook bzw. Meta veröffentlichte im Jahr 2023 das kostenfreie Modell LLaMA und verschiedene Varianten davon.
Ende 2025 veröffentlichte OpenAI die GPT-OSS Modelle. Sie sind unter der „Permissive License“ von Apache 2.0 lizenziert und können konfiguriert werden, beispielsweise hinsichtlich des Aufwands für Argumentation oder der Parameter. Weitere „Open-Weight“ Modelle sind: SmolLM3, Intellect 3, NHermes 4 u. dgl.

### Lokale LLMs

Es besteht die Möglichkeit, vortrainierte LLMs lokal auf einem PC oder einer Workstation auszuführen. Beispiele sind:

Alibaba Qwen3
DeepSeek V3
Google Gemma 3
GPT-OSS
Mistral AI - Mistral 3
Software, die lokale LLMs unterstützen, sind:

Hugging Face
Ollama
LM Studio
GPT4All

## LLM-Technologie

### Benchmarking

Für das Benchmarking kommen verschiedene Softwareartefakte zum Einsatz, die sich teilweise (seit den 2020er Jahren) selbst in Entwicklung befinden:

American Invitational Mathematics Examination (AIME)
Biomedical Text Mining (BioNLP)
Die Plattform Chatbot Arena
Elo-Zahl
GPQA Diamond, ein Multiple-Choice-Test in MINT-Fächern
HumanEval
Logical Reasoning Test
Massive Multitask Language Understanding (MMLU) – vgl. Genauigkeit
ML.ENERGY Benchmark – Energieverbrauch von LLMs
TruthfulQA – vgl. Halluzination

#### Leistungsmetriken

Bei den Leistungsdaten der KI-optimierten Hardware werden teilweise die üblichen Leistungsangaben in Floating Point Operations Per Second (FLOPS) veröffentlicht. Dabei handelt es sich nur um die arithmetische Operationen im Integer-(INT-) oder Fließkomma-(FP-)Format. Grundsätzlich werden zum Computerhardware-Benchmarking die folgenden Leistungsparameter von Mikroprozessoren oder Mikrocontrollern vermessen:

Dhrystone MIPS (DMIPS)
Gleitkommaoperationen pro Sekunde (FLOPS)
Instruktionen per Befehl (IPC)
Instruktionen pro Sekunde (IPS)
Insbesondere die IPS dienen aufgrund stagnierender Taktfrequenzzuwächse in Zyklen (Hz) oder Taktraten der CPU als wichtiger Benchmarkwert. Dies trifft vor allem auf Mehrkernprozessoren zu (siehe auch die Evolution der Rechenleistung der Mikroprozessoren, wobei CPUs nicht gleichzusetzen sind mit GPUs).
Im Falle von KI-optimierten IC-Bausteinen, z. B Mikrocontrollern (als Chips sind sie den „KI-Beschleunigern“ zuzuordnen), existieren außerdem folgende Größen bzw. Metriken:

GOPS oder GOP/s – Giga operations per second, und die nächste Größenordnung
TOPS oder TOP/s – Tera/trillion operations per second
Hier stehen die Operations für jede arithmetische oder logische Operation, häufig im Integer- oder Fließkomma-(FP-)Format, also z. B. 8-Bit INT/FP, 16-Bit INT/FP usw. Grundlegend sind die Operationen abhängig von der Bit-Größe. Mit anderen Worten: Mit 4-Bit-FP lassen sich höhere Rechengeschwindigkeiten erreichen. Je nach Hersteller wird eine Leistungsangabe in xOPS für verschiedene INT/FP-Kombinationen veröffentlicht.
Kleine Chip-Beschleuniger (KI-Koprozessoren von Mikrocontroller) haben Leistungsangaben von beispielsweise 256 GOPS, gemessen in 8-Bit-MACs/Zyklus bei 2 GHz. Dabei stehen die MAC für Multiply-Accumulate-Operationen. Eine MAC-Operation (Multiplikation mit folgender Addition) zählt als zwei FLOP-Operationen. Zwei weitere Beispiele für typische Benchmarks:

Nvidia H200 GPU: 4 PetaFLOPS (FP8) bei bis zu 700 W (TDP)
NXP Ara240 NPU: 40 äquivalente TOPS bei 6,5 W
Die Rechengeschwindigkeiten für KI-Anwendungen und die Stromaufnahme der Geräte könnten nicht unterschiedlicher sein. Da die Geräte jedoch ganz unterschiedliche Spezifikationen haben, sind auch ihre Einsatzgebiete unterschiedlich. Die Messwerte können nicht verglichen oder umgerechnet werden. Bei gleichem Format (z. B. FP8) kann man abschätzen: 1 MAC 
$\approx $

 2 × FLOP, jedoch können grundsätzlich die Metriken OPS nicht mit den FLOPS verglichen werden, also xOPS 
$\neq $

 xFLOPS.
Aufgrund der Komplexität des Themas hat sich 2018 die MLCommons-Organisation gebildet. Sie versucht eine Vielzahl von Standards zu erarbeiten. Dazu zählen Benchmarks für KI-Algorithmen, Training und Inferenz, für mobile Anwendungen (Smartphone), für eingebettete Anwendungen (Tiny), Sicherheit usw.

### Inferenz

Eine Vielzahl von Softwareartefakten zur Inferenz von LLMs existieren:

SGLang
LMDeploy
TRT-LLM
vLLM
LightLLM
Spezialisierte Software für AMD oder andere Hardware (vgl. „KI-Beschleuniger“)

### Multimodal Learning

Multimodal Learning verwendet verschieden strukturierte Daten im Bereich der künstlichen Intelligenz:

Text ist eine der am häufigsten verwendeten Modalitäten im maschinellen Lernen. Textdaten enthalten strukturierte Informationen, und mithilfe der natürlichen Sprachverarbeitung lässt sich leicht Wissen aus ihnen extrahieren. Die Techniken, die zur Verarbeitung dieser Informationen verwendet werden, umfassen Tokenisierung, Lemmatisierung, Syntaxanalyse, Erkennung von benannten Entitäten und Textklassifizierung.
Bilder sind eine wesentliche Quelle visueller Informationen. Mithilfe von Convolutional Neural Networks konnten große Fortschritte beim Verständnis von Bildern erzielt werden. Verwendete Techniken sind z. B. die Objekterkennung, die Gesichtserkennung und die Segmentierung von Bildern.
Die Audiomodalität umfasst Informationen aus Sprachaufnahmen, Tondateien oder Live-Streams.
Videos sind eine leistungsstarke Quelle für multimodale Daten, weil sie visuelle und auditive Informationen kombinieren. Computer Vision und Audioverarbeitungstechniken ermöglichen es, Wissen aus einer Videosequenz zu extrahieren. Dies ermöglicht die Erkennung von sich bewegenden Objekten, die Analyse menschlicher Aktivitäten oder sogar die Erkennung von Gesten.

### Bootstrapping Language-Image Pretraining

Die meisten modernen Vision-Language-Modelle benötigen während des Trainings einen hohen Rechenaufwand, weil das Training mit umfangreichen Modellen und Datensätzen erfolgt, vgl. Contrastive Language-Image Pre-training (CLIP). Die Forschung befindet sich an der Schnittstelle zwischen Sehen und Sprache. Daher ist zu erwarten, dass Vision-Language-Modelle von den leicht verfügbaren unimodalen Modellen der Bilderkennung und natürlichen Spracherkennung profitieren können.
Vortrainierte Vision-Modelle bieten eine qualitativ hochwertige visuelle Darstellung. Vortrainierte Sprachmodelle, insbesondere große Sprachmodelle, bieten leistungsstarke Fähigkeiten zur Sprachgenerierung und Zero-Shot-Übertragung. Um die Kosten zu senken und dem Problem des katastrophalen Vergessens entgegenzuwirken, bleiben die unimodalen vortrainierten Modelle während des Vortrainings eingefroren. Weil große Sprachmodelle jedoch während ihres unimodalen Vortrainings keine Bilder gesehen haben, macht das Einfrieren die visuelle Sprachausrichtung besonders schwierig.

### Skalierungsgesetze

Im Rahmen des maschinellen Lernens (ML) bzw. des tiefen Lernens (DL) analysieren Forscher die Leistung künstlicher neuronaler Netze (KNN). Dazu werden verschiedene empirische bzw. theoretische Potenzgesetze erforscht, die sich durch die Veränderung von Schlüsselfaktoren auf die Leistung der Berechnungen auswirken. Es handelt sich um Methoden zur Messung der Leistung von KNN und auch LLMs. Man spricht in diesem Zusammenhang auch von Metriken.
Viele KI-Modelle lassen sich durch vier Parameter beschreiben: (1) die Anzahl der Parameter (Modellgröße ohne MoE-Architektur) N, (2) die Größe des Datensatzes D, (3) die Berechnungskosten des Trainings (Zeit) C und (4) die Verluste oder Fehlerrate L. Die vier (oder mehr) Größen werden durch reelle Zahlen (Fließkommazahlen) definiert. Je nach Untersuchungsgegenstand existieren auch viele weitere Variablen.
Für das Training des GPT-3 Modells wurde beispielsweise das Gesetz 
$L=L_{0}+(C_{0}/C)^{0.048}$

 bestätigt.
Unterschiede ergeben sich für die Modellarchitektur (Funktionen und Komplexität der genutzten Algorithmen), beispielsweise bei der MoE-Architektur oder bei den Trainingsdaten, die in Vortraining und Feintraining aufgeteilt wurden. Das heißt, die meisten der oben genannten Faktoren hängen von anderen Variablen ab. Die Leistung eines Modells wird anhand seiner Fähigkeit bewertet, den Output anhand gegebener Eingangsdaten präzise vorherzusagen. Für LLMs nutzt man hierfür die logarithmische Plausibilitätsfunktion (der Logarithmus der Perplexität).
Das Thema „Skalierungsgesetze“ fällt in den Bereich der laufenden Forschung. KI-Wissenschaftler erforschen und testen verschiedene neuronale Potenzgesetze.

### Kollaps

Bei LLM und Foundation Models anderer Art (VAE, GMM) kann es durch das andauernde Training in der laufenden Nutzung zur dauerhaften, bis zur Unbrauchbarkeit reichenden Verschlechterung der Ergebnisqualität kommen. Man spricht auch von einem sogenannten Modellkollaps.
Dies betrifft insbesondere nachfolgende Modellversionen, die mit einem zunehmenden Anteil an künstlich generierten Daten trainiert werden, d. h., dass Teile der Trainingsdaten ebenfalls von einem LLM stammen. Eine Vorsortierung der in der Regel durch Webscraping erlangten Daten erscheint bisher als zu aufwändig.

### Testing und Qualität

Aufgrund der nichtdeterministischen Natur von KI-Modellen ergeben sich auch neue Herausforderungen für die Verifizierung und Validierung durch das Testen und die Qualität. Die komplexen Zusammenhänge zwischen Eingabe und Ausgabe lassen keine einfachen Rückschlüsse auf die Fähigkeiten zu. Aussagen wie „denkt wie ein Mensch“ sind nicht zu verifizieren. Ebenso wird KI von einzelnen Unternehmen als primäres Geschäftsmodell verstanden, weshalb Kritik als hinderlich angesehen wird.

## Glossar und Abkürzungen

## Auswirkungen und Kontroversen

### Bedrohungen durch KI/LLMs

Eine ausführliche, LLM-übergeordnete Kontroverse fand 2023 im Rahmen des Diskurses „Existenzielles Risiko durch künstliche Intelligenz“ statt.

### Ressourcenbedarf

Die Anforderungen an die Computerhardware (Halbleiterprodukte, speziell die Grafikprozessoren und Halbleiterspeicher High Bandwidth Memory (HBM), wie weiter oben ausgeführt) sowie der Energiebedarf, zunächst für das Training und später die Inferenz eines LLMs (z. B. via ChatGPT oder generell per API), sind für diese Technologie und die gesamte IT-Branche einzigartige Herausforderungen. Der Token-Verbrauch hatte sich seit Beginn der KI-Nutzung exzessive gesteigert. Der agentisch bedingte Token-Verbrauch überstieg im Februar 2026 den durch direkte menschliche Anfragen. Grund ist der um den Faktor 15 höhere Token-Bedarf bei agentischen Anfragen.
Mit dem gestiegenen Strombedarf wird erneut über nuklear erzeugte Energie diskutiert. Selbst über den mögliche Einsatz von Small Modular Reactors (SMR) mit ihren deutlich höheren Stromgestehungskosten wird nachgedacht. Gleichzeitig erfordert der Energiebedarf erhöhte Anstrengungen bei den technischen Speichermöglichkeiten und der intelligenten Abstimmung zu der zeitlich variierenden Energiebereitstellung aus nachhaltigen Quellen.

### Sicherheitsaspekte

US-Präsident Joe Biden erklärte: „Künstliche Intelligenz (KI) birgt sowohl Chancen als auch Risiken.“ Er ordnete im Jahr 2023 den Executive Order (EO) 14110 „Executive Order on Safe, Secure, and Trustworthy Development and Use of Artificial Intelligence“ an.
Die LLM-Softwaretechnologie hat Einfluss auf verschiedene soziale, wirtschaftliche und politische Themen. Die Medien sprechen von einem „Wettrüsten“ beim geplanten Einsatz von KI für militärische Zwecke (vgl. der Abschnitt KI-gestützte Kriegsführung). Dieses Aufrüsten bezieht sich im Speziellen auf die Computerhardware (vgl. auch „KI-Beschleuniger“) sowie die KI-Modelle und ihren automatisierten Verarbeitungsfähigkeiten. Aus Sicherheitsgründen wird die Weitergabe modernste Halbleitertechnologie durch Exportkontrollen eingeschränkt, beispielsweise von US-Technologie an China.
Das im April 2026 von Anthropic entwickelte Modell „Mythos“ wurde angekündigt, aber nicht der Öffentlichkeit zugänglich gemacht. Anthropic argumentierte, dass das Modell über Fähigkeiten im Bereich Cybersecurity verfügt, die ein Sicherheitsrisiko darstellen würden. In ersten Tests entdeckte das Modell Zero-Day-Schwachstellen, die teilweise seit zwanzig Jahren offen standen. Andererseits sehen Fachleute auch die Chance, mit dem Modell Angriffe besser abwehren zu können.

### Erkennung von Inhalten, die durch LLM generiert wurden

Es gibt verschiedene Anbieter von Tools zur Klassifikation, die versprechen, durch LLMs generierte Inhalte mit hoher Genauigkeit erkennen zu können. Diese Methoden arbeiten selbst mit künstlicher Intelligenz und liefern daher nur Anhaltspunkte, keine echten Beweise. Welche Merkmale eines Textes genau betrachtet werden, ist dabei nicht ersichtlich. Die beworbenen hohen Erkennungsgenauigkeiten beziehen sich oftmals nur auf vorher festgelegte Testdatensätze, die unter Laborbedingungen ausgewertet werden. Inwiefern sich diese auch auf Alltagssituationen „im echten Leben“ übertragen lassen, ist umstritten. Die verwendeten Testdatensätze werden als zu eingeschränkt kritisiert; Modelle, die für einen bestimmten Datensatz trainiert wurden, erreichen oft deutlich niedrigere Erkennungsraten auf anderen Datensätzen anderer Anbieter. Eine besondere Benachteiligung von Menschen, die nicht in ihrer Muttersprache schreiben bzw. weniger sprachgewandt sind, und deren Texte deshalb statistisch häufiger falsch positiv klassifiziert werden könnten, wird kritisch diskutiert.
