## Question 3: Include numerical/categorical data with a language model

Hello Hugging Face! I have been using transformers to gauge whether product reviews are
good or bad and so far, I have gotten decent results. I have information about how many
products the user has purchased in the past, how many times users spend looking at that
review, and a few other variables. Can we combine both the textual data with the numerical and
categorical data? Can you provide an example of how this could be done? I have a feeling that
this might produce the best results.


## Solution:

Yes, it is definitely possible to combine textual data with both numerical and categorical data with a language model.

For simplicity, let’s imagine the reviews dataset contains four different columns:

I) `reviews`: is a string that contains the actual review,

II) `number_of_products`:  is number of products a certain user has purchased in the past.

III) `number_of_times`:  is number of times a user spent looking at the review.

IV) `type_of_product`: is a string represents the category of the product and can only take finite values. E.g. Jeans, Shirts, Dress, etc.

I can think of these two different ways in which they can be merged together to get better results. The first one is easier and the second one is a bit more complex. I will explain both of them below.

### Concatenating numerical and categorical data as string with textual data

In this approach, the numerical and categorical data are converted to strings and then concatenated together with the text. This unified representation allows us to provide comprehensive input to the model. It can look something like this:

``` python
from datasets import Dataset

# Example data
data = {
    'reviews': ["This product is great!", "Not satisfied with this product."],
    'number_of_products': [3, 1],
    'number_of_times': [5, 2],
    'type_of_product': ["Jeans", "Shirts"]
}

# Create a dataset using HuggingFace datasets library
dataset = Dataset.from_dict(data)

# Combine numerical and categorical data as text, including insights
def combine_data(row):
    return {'concat_review': (
        f"This user has purchased {row['number_of_products']} products. "
        f"This review was viewed {row['number_of_times']} times. "
        f"The product that has been reviewed belongs to the category {row['type_of_product']}. "
        f"Review of the product: {row['Reviews']}"
    )}

# Map the combine_data function to the dataset
dataset = dataset.map(combine_data, remove_columns=['reviews', 'number_of_products', 'number_of_times', 'type_of_product'])

print(dataset['concat_review'][0])
```

The same code can also be found in the `solution.ipynb` notebook.

Output from the above code will look like this:

``` python
This user purchased has purchased 3 products. This review was viewed 5 times. The product that has been reviewed belongs to the category Jeans. This product is great.
```

With this approach, one can replace the `reviews` with `concat_review` as input in their current modeling setup.

The problem with this approach is that the model will have to learn to extract the relevant information from the concatenated string. This can be a bit challenging for the model to learn if the dataset size is small and also depends on the transformer model architecture. It might be possible that given a large enough dataset, the transformer model can start picking up these features. However, it is not guaranteed that the model will learn to extract the relevant information from the concatenated string.


### Concatenating numerical and categorical features with textual features

In this approach, we concatenate features instead of the raw data. We leverage different feature extractors:

1. **Text Feature Extraction:** We begin by extracting features from the text data using a transformer-based language model, which enables us to capture rich contextual information from the text. As it is text classification, we will extract the [CLS] embedding from a transformer Language Model.

2. **Numerical Data Handling:** For numerical data, we retain the raw numeric values as their representation, preserving their inherent information.

3. **Categorical Data Representation:** For categorical data, we have two options:
    - **One-Hot Encoding:** We can employ one-hot encoding to represent categorical variables, ensuring each category is expressed as a binary vector.
    - **Vector Representation:** Alternatively, we can use specialized models like Word2Vec to obtain vector representations of categorical categories. This approach transforms categories into continuous vectors, facilitating their integration with numerical and textual data.

After extracting the relevant features, we **concatenate** them across the last dimension, creating a unified representation.
For **Model Training** utilize this unified representation as input to a Multilayer Perceptron (MLP) model.

  ![image](https://user-images.githubusercontent.com/18352477/266776140-f604ec0c-e35d-4d94-bdc9-2cc9a3a14c96.png)

The code for this approach can be found in the `solution.ipynb` Notebook.

With this approach, we are explicitly providing the model with the relevant information and it does not have to learn to extract the relevant information from the concatenated string. This approach is also more flexible as it allows us to use different feature extractors for numerical and categorical data. For example, we can use one-hot encoding or Word2Vec for categorical data. At the same time we can also use some weighting scheme to give more importance to the text data. For example, we can use a weighted sum of the text, numerical and categorical data. This approach is more flexible and allows us to experiment with different feature extractors and weighting schemes.

Also, one can normalize the numerical features before concatenating it with the text features. This will ensure that the numerical features is on the same scale as the text features.

