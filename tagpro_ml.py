import os
import tensorflow as tf
tf.enable_eager_execution()
from data_collection import tagpro_data_to_tensorflow_dataset

if __name__ == "__main__":   

    training_data = tagpro_data_to_tensorflow_dataset("rolling_300_data")
    testing_data = tagpro_data_to_tensorflow_dataset()

    model = tf.keras.Sequential([
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dense(1),
    ])

    model.compile(
        loss=tf.keras.losses.BinaryCrossentropy(from_logits=True),
        optimizer='adam',
        metrics=['accuracy'])

    model.fit(training_data, epochs=100)

    test_loss, test_accuracy = model.evaluate(testing_data)

    print('\n\nTest Loss {}, Test Accuracy {}'.format(test_loss, test_accuracy))

    predictions = model.predict(testing_data)

    for prediction, survived in zip(predictions[:10], list(testing_data)[0][1][:10]):
        prediction = tf.sigmoid(prediction).numpy()
        print("Predicted won: {:.2%}".format(prediction[0]),
                " | Actual outcome: ",
                ("Won" if bool(survived) else "Lost"))
