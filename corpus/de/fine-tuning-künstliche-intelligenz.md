---
title: Fine-Tuning (Künstliche Intelligenz)
url: https://de.wikipedia.org/wiki/Fine-Tuning_(K%C3%BCnstliche_Intelligenz)
updated: '2026-05-09T20:03:25Z'
language: de
revision: '266929943'
license: CC BY-SA 4.0
source: Wikipedia
---

Fine-Tuning (deutsch: Feinabstimmung) ist in der künstlichen Intelligenz, insbesondere bei Deep Learning, ein Begriff, unter dem man eine Methode des Lerntransfers eines vortrainierten künstlichen neuronalen Netzwerks versteht. Ein Beispiel ist die Entwicklung von GPT-3 durch OpenAI. Foundation Models (Basismodelle) sind maschinelle Lernmodelle, welche auf einer großen Menge von Daten vortrainiert werden. Sie ermöglichen es, durch Feinabstimmung solche Modelle auf spezifische Aufgaben oder Anwendungsfälle anzupassen und zu optimieren.
Häufig dienen Large Language Models (LLM) als textbasierte Basismodelle, welche insbesondere für die Sprach- und Bildverarbeitung multimodal weiterentwickelt wurden. Auch können Unternehmen eine Lizenz für ein geeignetes Modell erwerben und durch Feinabstimmung mittels firmeneigener Daten für spezifische Aufgaben optimierte Lösungen erarbeiten. Dabei wird zu einer bestimmten Anfrage (Prompt) die gewünschte Antwort vorgegeben und mit dem Ergebnis des Modells verglichen. Abweichungen werden ins Modell zur Korrektur eingespeist.

## Techniken

Die Feinabstimmung erfolgt in der Regel durch überwachtes Lernen (englisch Supervised Fine-tuning). Hierbei werden die Parameter eines vortrainierten Modells auf neue Daten trainiert und entsprechend angepasst. In der Regel werden dazu diskriminative, statistische Methoden verwendet. Dies kann für das gesamte neuronale Netz oder nur für einen Teil der Schichten erfolgen.
Um den Aufwand für Rechenzeit und Speicherbedarf tief zu halten, gibt es unterschiedliche Techniken:

### Low-rank Adaptation (LoRA)

Low-Rank Adaptation (LoRA) ist eine Methode zur effizienten Feinabstimmung von Modellen. Sie wurde ursprünglich von einem Team von Microsoft-Forschern im Jahr 2021 eingeführt. Dabei wird das vortrainierte Modell mit seinen bestehenden Parametern eingefroren. Dann werden kleinere, trainierbare Rangzerlegungs-Matrizen zu niederrangigen, nachgelagerten Schichten (neben den ursprünglichen Matrizen) der neuronalen Struktur zugefügt, um die Zahl der zusätzlich für die Abstimmung trainierbaren Parameter in den nachfolgenden Schichten tief zu halten. Seitdem hat die LoRA-Methode sich zu einem beliebten Ansatz für die Abstimmung von LLMs (großer Sprachmodelle), Diffusionsmodelle (z. B. für die Bildgenerierung) und anderer Arten von KI-Modellen entwickelt. Weiterentwicklungen erfolgen z. B. durch den Einsatz der Fourier-Transformation.

### Representation Fine-Tuning (ReFT)

Representation Fine-Tuning (ReFT) ist eine Technik, die von Forschern der Stanford University entwickelt wurde, um große Sprachmodelle durch die Modifikation von weniger als 1 % ihrer Repräsentationen feinabzustimmen. Im Gegensatz zu traditionellen, parameter-effizienten Feinabstimmungsmethoden wie Low-rank Adaptation, die sich hauptsächlich auf die Aktualisierung von Gewichten konzentrieren, zielt ReFT auf spezifische Teile des Modells ab, die für die Aufgabe der Feinabstimmung relevant sind. Dieser Ansatz basiert auf der Erkenntnis, dass Deep-Learning-Modelle reichhaltige semantische Informationen in ihren Repräsentationen kodieren. Modifikation von Repräsentationen sind möglicherweise eine effektivere Strategie als die Aktualisierung von Gewichtsparametern. ReFT-Methoden arbeiten mit einem eingefrorenen Basismodell und lernen auf verdeckten Repräsentationen aufbauenden, aufgabenbezogenen Eingriffen. Diese Eingriffe manipulieren einen kleinen Teil der Modellrepräsentationen, um das Verhalten des Modells bei der Lösung nachgelagerter Aufgaben zu steuern.

### Weitere Techniken

Um festgestellte Nachteile bestimmter Fine-Tuning-Methoden zu vermeiden, werden Verbesserungen erforscht.
