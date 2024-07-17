import tensorflow as tf
from tensorflow.keras import layers

class NBeatsBlock(tf.keras.layers.Layer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.hidden1 = tf.keras.layers.Conv1D(filters=f1, kernel_size=k1, activation='relu')
        self.hidden2 = tf.keras.layers.Conv1D(filters=f2, kernel_size=k2, activation='relu')
        self.hidden3 = tf.keras.layers.Conv1D(filters=f3, kernel_size=k3, activation='relu')

        self.pool1 = tf.keras.layers.MaxPooling1D(pool_size=p1)
        self.pool2 = tf.keras.layers.MaxPooling1D(pool_size=p2)
        self.pool3 = tf.keras.layers.MaxPooling1D(pool_size=p3)

        self.flat1 = tf.keras.layers.Flatten()
        self.dense1 = tf.keras.layers.Dense(d1, activation='relu')

    def call(self, inputs):
        x = inputs
        x = self.hidden1(x)
        x = self.pool1(x)
        x = self.hidden2(x)
        x = self.pool2(x)
        x = self.hidden3(x)
        x = self.pool3(x)
        x = self.flat1(x)
        x = self.dense1(x)
        return x

def build_model(input_shape, num_blocks, output_size):
    stack_input = layers.Input(shape=input_shape, name="stack_input")
    residual = stack_input
    forecasts = []

    for i in range(num_blocks):
        nbeats_block = NBeatsBlock(name=f"Block{i+1}")
        backcast = nbeats_block(residual)
        
        dense1 = layers.Dense(d2, activation='relu')(backcast)
        dense2 = layers.Dense(d3, activation='relu')(dense1)
        forecast = layers.Dense(output_size, activation='softmax', name=f"forecast{i+1}")(dense2)
        forecasts.append(forecast)

        dense_backcast = layers.Dense(input_shape[0], activation='relu')(backcast)
        reshaped_backcast = layers.Reshape(input_shape)(dense_backcast)
        residual = layers.subtract([residual, reshaped_backcast])

    residual = layers.Flatten(name="out1")(residual)
    output_main = layers.Average(name="out2")(forecasts)

    model = tf.keras.Model(inputs=stack_input, outputs=[residual, output_main])
    return model

if __name__ == "__main__":
    model_nb = build_model(input_shape, num_blocks, output_size)
    model_nb.summary()