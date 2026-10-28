---
title: Residual neural network
url: https://en.wikipedia.org/wiki/Residual_neural_network
updated: '2026-09-24T02:21:51Z'
language: en
revision: '1376425875'
license: CC BY-SA 4.0
source: Wikipedia
---

A residual neural network (also referred to as a residual network or ResNet) is a deep learning architecture in which the layers learn residual functions with reference to the layer inputs. It was developed in 2015 for image recognition, and won the ImageNet Large Scale Visual Recognition Challenge (ILSVRC) of that year.
As a point of terminology, "residual connection" refers to the specific architectural motif of 
$x\mapsto f(x)+x$

, where 
$f$

 is an arbitrary neural network module. The motif had been used previously (see §History for details). However, the publication of ResNet made it widely popular for feedforward networks, appearing in neural networks that are seemingly unrelated to ResNet.
The residual connection stabilizes the training and convergence of deep neural networks with hundreds of layers, and is a common motif in deep neural networks, such as transformer models (e.g., BERT, and GPT models such as ChatGPT), the AlphaGo Zero system, the AlphaStar system, and the AlphaFold system.

## Mathematics

### Residual connection

In a multilayer neural network model, consider a (non-residual) subnetwork with a certain number of stacked layers (e.g., 2 or 3). Let 
$H(x;\alpha )$

 denote the subnetwork, where 
$x$

 is the input and 
$\alpha $

 is the set of parameters. Suppose 
$H^{*}$

 is the desired optimal output of this subnetwork. Residual learning simply adds 
$x$

 directly to the output, such that the optimal learned output now becomes 
$H^{*}-x$

, which is interpreted as a "residual" with respect to 
$x$

.
The operation of "adding 
$x$

" is implemented via a "skip connection" that performs an identity mapping to connect the input of the subnetwork with its output. This connection is referred to as a "residual connection" in later work.
Let 
$F(x;\alpha )=H(x;\alpha )+x$

. The function 
$F$

 is often represented by matrix multiplication interlaced with activation functions and normalization operations (e.g., batch normalization or layer normalization). As a whole, one of these subnetworks is referred to as a "residual block". A deep residual network is constructed by simply stacking these blocks.
Long short-term memory (LSTM) has a memory mechanism that serves as a residual connection. In an LSTM without a forget gate, an input 
$x_{t}$

 is processed by a function 
$F$

 and added to a memory cell 
$c_{t}$

, resulting in 
$c_{t+1}=c_{t}+F(x_{t})$

. An LSTM with a forget gate essentially functions as a highway network.
To stabilize the variance of the layers' inputs, it is recommended to replace the residual connections 
$x+f(x)$

 with 
$x/L+f(x)$

, where 
$L$

 is the total number of residual layers.

### Projection connection

If the function 
$F$

 is of type 
$F:\mathbb {R} ^{n}\to \mathbb {R} ^{m}$

 where 
$n\neq m$

, then 
$F(x)+x$

 is undefined. To handle this special case, a projection connection is used:

$y=F(x)+P(x)$

where 
$P$

 is typically a linear projection, defined by 
$P(x)=Mx$

 where 
$M$

 is a 
$m\times n$

 matrix. The matrix is trained via backpropagation, as is any other parameter of the model.

### Signal propagation

The introduction of identity mappings facilitates signal propagation in both forward and backward paths.

#### Forward propagation

If the output of the 
$\ell $

-th residual block is the input to the 
$(\ell +1)$

-th residual block (assuming no activation function between blocks), then the 
$(\ell +1)$

-th input is:

$x_{\ell +1}=F(x_{\ell })+x_{\ell }$

Applying this formulation recursively, e.g.:

${\begin{aligned}x_{\ell +2}&=F(x_{\ell +1})+x_{\ell +1}\\&=F(x_{\ell +1})+F(x_{\ell })+x_{\ell }\end{aligned}}$

yields the general relationship:

$x_{L}=x_{\ell }+\sum _{i=\ell }^{L-1}F(x_{i})$

where 

        L

    {\textstyle L}

 is the index of a residual block and 

        ℓ

    {\textstyle \ell }

 is the index of some earlier block. This formulation suggests that there is always a signal that is directly sent from a shallower block 

        ℓ

    {\textstyle \ell }

 to a deeper block 

        L

    {\textstyle L}

.

#### Backward propagation

The residual learning formulation provides the added benefit of mitigating the vanishing gradient problem to some extent. However, it is crucial to acknowledge that the vanishing gradient issue is not the root cause of the degradation problem, which is tackled through the use of normalization. To observe the effect of residual blocks on backpropagation, consider the partial derivative of a loss function 
${\mathcal {E}}$

 with respect to some residual block input 
$x_{\ell }$

. Using the equation above from forward propagation for a later residual block 
$L>\ell $

:

${\begin{aligned}{\frac {\partial {\mathcal {E}}}{\partial x_{\ell }}}&={\frac {\partial {\mathcal {E}}}{\partial x_{L}}}{\frac {\partial x_{L}}{\partial x_{\ell }}}\\&={\frac {\partial {\mathcal {E}}}{\partial x_{L}}}\left(1+{\frac {\partial }{\partial x_{\ell }}}\sum _{i=\ell }^{L-1}F(x_{i})\right)\\&={\frac {\partial {\mathcal {E}}}{\partial x_{L}}}+{\frac {\partial {\mathcal {E}}}{\partial x_{L}}}{\frac {\partial }{\partial x_{\ell }}}\sum _{i=\ell }^{L-1}F(x_{i})\end{aligned}}$

This formulation suggests that the gradient computation of a shallower layer, 

              ∂

                  E

              ∂

                x

                  ℓ

    {\textstyle {\frac {\partial {\mathcal {E}}}{\partial x_{\ell }}}}

, always has a later term 

              ∂

                  E

              ∂

                x

                  L

    {\textstyle {\frac {\partial {\mathcal {E}}}{\partial x_{L}}}}

 that is directly added. Even if the gradients of the 
$F(x_{i})$

 terms are small, the total gradient 

              ∂

                  E

              ∂

                x

                  ℓ

    {\textstyle {\frac {\partial {\mathcal {E}}}{\partial x_{\ell }}}}

 resists vanishing due to the added term 

              ∂

                  E

              ∂

                x

                  L

    {\textstyle {\frac {\partial {\mathcal {E}}}{\partial x_{L}}}}

.

## Variants of residual blocks

### Basic block

A basic block is the simplest building block studied in the original ResNet. This block consists of two sequential 3x3 convolutional layers and a residual connection. The input and output dimensions of both layers are equal.

### Bottleneck block

A bottleneck block consists of three sequential convolutional layers and a residual connection. The first layer in this block is a 1×1 convolution for dimension reduction (e.g., to 1/2 of the input dimension); the second layer performs a 3×3 convolution; the last layer is another 1×1 convolution for dimension restoration. The models of ResNet-50, ResNet-101, and ResNet-152 are all based on bottleneck blocks.

### Pre-activation block

The pre-activation residual block applies activation functions before applying the residual function 
$F$

. Formally, the computation of a pre-activation residual block can be written as:

$x_{\ell +1}=F(\phi (x_{\ell }))+x_{\ell }$

where 
$\phi $

 can be any activation (e.g. ReLU) or normalization (e.g. LayerNorm) operation. This design reduces the number of non-identity mappings between residual blocks, and allows an identity mapping directly from the input to the output. This design was used to train models with 200 to over 1000 layers, and was found to consistently outperform variants where the residual path is not an identity function. The pre-activation ResNet with 200 layers took 3 weeks to train for ImageNet on 8 GPUs in 2016.
Since GPT-2, transformer blocks have been mostly implemented as pre-activation blocks. This is often referred to as "pre-normalization" in the literature of transformer models.

## Applications

Originally, ResNet was designed for computer vision.
All transformer architectures include residual connections. Indeed, very deep transformers cannot be trained without them.
The original ResNet paper made no claim on being inspired by biological systems. However, later research has related ResNet to biologically-plausible algorithms.
A study published in Science in 2023 disclosed the complete connectome of an insect brain (specifically that of a fruit fly larva). This study discovered "multilayer shortcuts" that resemble the skip connections in artificial neural networks, including ResNets.

## History

### Previous work

Residual connections were noticed in neuroanatomy, such as Lorente de No (1938). McCulloch and Pitts (1943) proposed artificial neural networks and considered those with residual connections.
In 1961, Frank Rosenblatt described a three-layer multilayer perceptron (MLP) model with skip connections. The model was referred to as a "cross-coupled system", and the skip connections were forms of cross-coupled connections.

During the late 1980s, "skip-layer" connections were sometimes used in neural networks. Examples include: Lang and Witbrock (1988) trained a fully connected feedforward network where each layer skip-connects to all subsequent layers, like the later DenseNet (2016). In this work, the residual connection was the form 
$x\mapsto F(x)+P(x)$

, where 
$P$

 is a randomly-initialized projection connection. They termed it a "short-cut connection". An early neural language model used residual connections and named them "direct connections".

### Degradation problem

Sepp Hochreiter discovered the vanishing gradient problem in 1991 and argued that it explained why the then-prevalent forms of recurrent neural networks did not work for long sequences. He and Schmidhuber later designed the LSTM architecture to solve this problem, which has a "cell state" 
$c_{t}$

 that can function as a generalized residual connection. The highway network (2015) applied the idea of an LSTM unfolded in time to feedforward neural networks, resulting in the highway network. ResNet is equivalent to an open-gated highway network.

During the early days of deep learning, there were attempts to train increasingly deep models. Notable examples included the AlexNet (2012), which had 8 layers, and the VGG-19 (2014), which had 19 layers. However, stacking too many layers led to a steep reduction in training accuracy, known as the "degradation" problem. In theory, adding additional layers to deepen a network should not result in a higher training loss, but this is what happened with VGGNet. If the extra layers can be set as identity mappings, however, then the deeper network would represent the same function as its shallower counterpart. There is some evidence that the optimizer is not able to approach identity mappings for the parameterized layers, and the benefit of residual connections was to allow identity mappings by default.
In 2014, the state of the art was training deep neural networks with 20 to 30 layers. The research team for ResNet attempted to train deeper ones by empirically testing various methods for training deeper networks, until they came upon the ResNet architecture.

### Subsequent work

Wide Residual Network (2016) found that using more channels and fewer layers than the original ResNet improves performance and GPU-computational efficiency, and that a block with two 3×3 convolutions is superior to other configurations of convolution blocks.
DenseNet (2016) connects the output of each layer to the input to each subsequent layer:

$x_{\ell +1}=F(x_{1},x_{2},\dots ,x_{\ell -1},x_{\ell })$

Stochastic depth is a regularization method that randomly drops a subset of layers and lets the signal propagate through the identity skip connections. Also known as DropPath, this regularizes training for deep models, such as vision transformers.
ResNeXt (2017) combines the Inception module with ResNet.
Squeeze-and-Excitation Networks (2018) added squeeze-and-excitation (SE) modules to ResNet. An SE module is applied after a convolution, and takes a tensor of shape 
$\mathbb {R} ^{H\times W\times C}$

 (height, width, channels) as input. Each channel is averaged, resulting in a vector of shape 
$\mathbb {R} ^{C}$

. This is then passed through a multilayer perceptron (with an architecture such as linear-ReLU-linear-sigmoid) before it is multiplied with the original tensor. It won the ILSVRC in 2017.
