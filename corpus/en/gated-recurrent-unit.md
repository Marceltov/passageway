---
title: Gated recurrent unit
url: https://en.wikipedia.org/wiki/Gated_recurrent_unit
updated: '2026-08-06T17:48:43Z'
language: en
revision: '1368041305'
license: CC BY-SA 4.0
source: Wikipedia
---

In artificial neural networks, the gated recurrent unit (GRU) is a gating mechanism used in recurrent neural networks, introduced in 2014 by Kyunghyun Cho et al. The GRU is like a long short-term memory (LSTM) with a gating mechanism to input or forget certain features, but lacks a context vector or output gate, resulting in fewer parameters than LSTM. 
GRU's performance on certain tasks of polyphonic music modeling, speech signal modeling and natural language processing was found to be similar to that of LSTM. GRUs showed that gating is indeed helpful in general, and Bengio's team came to no concrete conclusion on which of the two gating units was better.

## Architecture

There are several variations on the full gated unit, with gating done using the previous hidden state and the bias in various combinations, and a simplified form called minimal gated unit.
In the following, the operator 
$\odot $

 denotes the Hadamard product.

### Fully gated unit

Initially, for 
$t=0$

, the output vector is 
$h_{0}=0$

. 

${\begin{aligned}z_{t}&=\sigma (W_{z}x_{t}+U_{z}h_{t-1}+b_{z})\\r_{t}&=\sigma (W_{r}x_{t}+U_{r}h_{t-1}+b_{r})\\{\hat {h}}_{t}&=\phi (W_{h}x_{t}+U_{h}(r_{t}\odot h_{t-1})+b_{h})\\h_{t}&=(1-z_{t})\odot h_{t-1}+z_{t}\odot {\hat {h}}_{t}\end{aligned}}$

Variables (
$d$

 denotes the number of input features and 
$e$

 the number of output features):

$x_{t}\in \mathbb {R} ^{d}$

: input vector

$h_{t}\in \mathbb {R} ^{e}$

: output vector

${\hat {h}}_{t}\in \mathbb {R} ^{e}$

: candidate activation vector

$z_{t}\in (0,1)^{e}$

: update gate vector

$r_{t}\in (0,1)^{e}$

: reset gate vector

$W\in \mathbb {R} ^{e\times d}$

, 
$U\in \mathbb {R} ^{e\times e}$

 and 
$b\in \mathbb {R} ^{e}$

: parameter matrices and vector which need to be learned during training
Activation functions

$\sigma $

: The original is a logistic function.

$\phi $

: The original is a hyperbolic tangent.
Alternative activation functions are possible, provided that 
$\sigma (x)\in [0,1]$

.

Alternate forms can be created by changing 
$z_{t}$

 and 
$r_{t}$

Type 1: each gate depends only on the previous hidden state and the bias.

${\begin{aligned}z_{t}&=\sigma (U_{z}h_{t-1}+b_{z})\\r_{t}&=\sigma (U_{r}h_{t-1}+b_{r})\\\end{aligned}}$

Type 2: each gate depends only on  the previous hidden state.

${\begin{aligned}z_{t}&=\sigma (U_{z}h_{t-1})\\r_{t}&=\sigma (U_{r}h_{t-1})\\\end{aligned}}$

Type 3: each gate is computed using only the bias.

${\begin{aligned}z_{t}&=\sigma (b_{z})\\r_{t}&=\sigma (b_{r})\\\end{aligned}}$

### Minimal gated unit

The minimal gated unit (MGU) is similar to the fully gated unit, except the update and reset gate vector is merged into a forget gate. This also implies that the equation for the output vector must be changed:

${\begin{aligned}f_{t}&=\sigma (W_{f}x_{t}+U_{f}h_{t-1}+b_{f})\\{\hat {h}}_{t}&=\phi (W_{h}x_{t}+U_{h}(f_{t}\odot h_{t-1})+b_{h})\\h_{t}&=(1-f_{t})\odot h_{t-1}+f_{t}\odot {\hat {h}}_{t}\end{aligned}}$

Variables

$x_{t}$

: input vector

$h_{t}$

: output vector

${\hat {h}}_{t}$

: candidate activation vector

$f_{t}$

: forget vector

$W$

, 
$U$

 and 
$b$

: parameter matrices and vector

### Light gated recurrent unit

The light gated recurrent unit (LiGRU) removes the reset gate altogether, replaces tanh with the ReLU activation, and applies batch normalization (BN):

${\begin{aligned}z_{t}&=\sigma (\operatorname {BN} (W_{z}x_{t})+U_{z}h_{t-1})\\{\tilde {h}}_{t}&=\operatorname {ReLU} (\operatorname {BN} (W_{h}x_{t})+U_{h}h_{t-1})\\h_{t}&=z_{t}\odot h_{t-1}+(1-z_{t})\odot {\tilde {h}}_{t}\end{aligned}}$

LiGRU has been studied from a Bayesian perspective. This analysis yielded a variant called light Bayesian recurrent unit (LiBRU), which showed slight improvements over the LiGRU on speech recognition tasks.
