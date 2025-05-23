"""
Implements a network visualization in PyTorch.
Make sure to write device-agnostic code. For any function, initialize new tensors
on the same device as input tensors
"""

import torch


def hello():
    """
    This is a sample function that we will try to import and run to ensure that
    our environment is correctly set up on Google Colab.
    """
    print("Hello from network_visualization.py!")


def compute_saliency_maps(X, y, model):
    """
    Compute a class saliency map using the model for images X and labels y.

    Input:
    - X: Input images; Tensor of shape (N, 3, H, W)
    - y: Labels for X; LongTensor of shape (N,)
    - model: A pretrained CNN that will be used to compute the saliency map.

    Returns:
    - saliency: A Tensor of shape (N, H, W) giving the saliency maps for the input
    images.
    """
    # Make input tensor require gradient
    X.requires_grad_()

    saliency = None
    ##############################################################################
    # TODO: Implement this function. Perform a forward and backward pass through #
    # the model to compute the gradient of the correct class score with respect  #
    # to each input image. You first want to compute the loss over the correct   #
    # scores (we'll combine losses across a batch by summing), and then compute  #
    # the gradients with a backward pass.                                        #
    # Hint: X.grad.data stores the gradients                                     #
    ##############################################################################
    # Replace "pass" statement with your code
    scores = model(X)
    loss = torch.nn.CrossEntropyLoss()(scores, y)
    loss.backward()
    
    saliency = X.grad.abs().max(dim=1)[0]
    ##############################################################################
    #               END OF YOUR CODE                                             #
    ##############################################################################
    return saliency


def make_adversarial_attack(X, target_y, model: torch.nn.Module, max_iter=100, verbose=True):
    """
    Generate an adversarial attack that is close to X, but that the model classifies
    as target_y.

    Inputs:
    - X: Input image; Tensor of shape (1, 3, 224, 224)
    - target_y: An integer in the range [0, 1000)
    - model: A pretrained CNN
    - max_iter: Upper bound on number of iteration to perform
    - verbose: If True, it prints the pogress (you can use this flag for debugging)

    Returns:
    - X_adv: An image that is close to X, but that is classifed as target_y
    by the model.
    """
    # Initialize our adversarial attack to the input image, and make it require
    # gradient
    X_adv = X.clone()
    X_adv = X_adv.requires_grad_()

    learning_rate = 1
    ##############################################################################
    # TODO: Generate an adversarial attack X_adv that the model will classify    #
    # as the class target_y. You should perform gradient ascent on the score     #
    # of the target class, stopping when the model is fooled.                    #
    # When computing an update step, first normalize the gradient:               #
    #   dX = learning_rate * g / ||g||_2                                         #
    #                                                                            #
    # You should write a training loop.                                          #
    #                                                                            #
    # HINT: For most examples, you should be able to generate an adversarial     #
    # attack in fewer than 100 iterations of gradient ascent.                    #
    # You can print your progress over iterations to check your algorithm.       #
    ##############################################################################
    # Replace "pass" statement with your code

    # NOTE: This one with cross entropy loss
    # cross_entropy = torch.nn.CrossEntropyLoss()
    # optimizer = torch.optim.Adam([X_adv], lr=learning_rate)

    # for epoch in range(max_iter):
    #     optimizer.zero_grad()

    #     scores = model(X_adv)
    #     loss = cross_entropy(scores, torch.tensor(target_y, dtype=torch.long).unsqueeze(0))

    #     with torch.no_grad():
    #         target_score = scores[:, target_y].item()
    #         max_score = torch.max(scores, dim=1)[0]
    #         print(f'Iteration %d: target score %.3f, max score %.3f' % (epoch, scores[:, target_y].item(), torch.max(scores, dim=1)[0]))
    #         if target_score == max_score:
    #             print('Mission is done!')
    #             break

    #     loss.backward()

    #     optimizer.step()

    # we want to maximize the score for targeted class

      
    
    # we want to maximize it, we have to do gradient ascent!
    

    for iteration in range(max_iter):
        X_adv.grad = None

        scores = model(X_adv)

        criterion = scores[:, target_y]
        criterion.backward()

        with torch.no_grad():
            X_adv += learning_rate * X_adv.grad.data / X_adv.grad.data.norm(p=2)

            if verbose and iteration % 5 == 0:
                target_score = scores[:, target_y].item()
                max_score = torch.max(scores, dim=1)[0]
                print(f'Iteration %d: target score %.3f, max score %.3f' % (iteration, target_score, max_score))
            if target_y == torch.argmax(scores, dim=1):
                print('Mission is done!')
                break
        
        
    ##############################################################################
    #                             END OF YOUR CODE                               #
    ##############################################################################
    return X_adv


def class_visualization_step(img, target_y, model, **kwargs):
    """
    Performs gradient step update to generate an image that maximizes the
    score of target_y under a pretrained model.

    Inputs:
    - img: random image with jittering as a PyTorch tensor
    - target_y: Integer in the range [0, 1000) giving the index of the class
    - model: A pretrained CNN that will be used to generate the image

    Keyword arguments:
    - l2_reg: Strength of L2 regularization on the image
    - learning_rate: How big of a step to take
    """

    l2_reg = kwargs.pop("l2_reg", 1e-3)
    learning_rate = kwargs.pop("learning_rate", 25)
    ########################################################################
    # TODO: Use the model to compute the gradient of the score for the     #
    # class target_y with respect to the pixels of the image, and make a   #
    # gradient step on the image using the learning rate. Don't forget the #
    # L2 regularization term!                                              #
    # Be very careful about the signs of elements in your code.            #
    # Hint: You have to perform inplace operations on img.data to update   #
    # the generated image using gradient ascent & reset img.grad to zero   #
    # after each step.                                                     #
    ########################################################################
    # Replace "pass" statement with your code

    scores = model(img)
    criterion = scores[:, target_y] - l2_reg * (img ** 2).sum()
    criterion.backward()

    with torch.no_grad():
        grad = img.grad
        # grad_norm suggested by chatgpt
        # grad_norm = grad / (grad.norm() + 1e-8)
        img += learning_rate * grad
        # this one is also suggested by chatgpt
        # img.clamp_(0, 1)
        img.grad.zero_()
    ########################################################################
    #                             END OF YOUR CODE                         #
    ########################################################################
    return img