import keras
from keras.models import Sequential
from keras import layers
from keras.layers.merge import add

# TODO
# For kernel size and stride, went from a single value 'n' to a tuple '(n,n)'. Need to make sure that this is the correct way to go from pytorch to keras
#def ResBlock(x, in_channels, out_channels):
def ResBlock(in_channels, out_channels):

    def f(x):
        residual = x

        downsample = out_channels//in_channels

        #TODO check the way that these layers are working, make sure it is done properly
        #TODO see if I want the batch normalization layers
        conv = layers.Conv2D(out_channels, input_shape=keras.backend.shape(x)[1:], activation='relu', kernel_size=(3,3), strides=(downsample,downsample), padding='SAME')(x)
        #conv = layers.BatchNormalization()(conv)
        conv = layers.Conv2D(out_channels, kernel_size=(3,3), padding='SAME')(conv)
        #conv = layers.BatchNormalization()(conv)
        #shortcut = layers.Conv2D(out_channels, kernel_size=1, strides=downsample)(x)

        if downsample > 1:
            #residual = shortcut
            residual = layers.Conv2D(out_channels, kernel_size=1, strides=downsample)(x)

        block = layers.Add()([conv, residual])
        #block = conv + residual
        block = layers.Activation('relu')(block)

        return block
    return f

#ResBlocks
#def block_layers(_x, _nblocks, _fmaps):
def block_layers(nblocks, fmaps):
    def f(x):
        for _ in range(nblocks):
            x = ResBlock(fmaps[0], fmaps[1])(x)
        return x
    return f


#def ResNet(in_channels, nblocks, fmaps):
class ResNet(object):

    @staticmethod
    def build(in_channels, nblocks, fmaps, input_shape=(125,125,3)):
        input = layers.Input(shape=input_shape)

        #conv0 - changed padding from 1 to 'SAME'
        x = layers.Conv2D(fmaps[0], input_shape=input_shape, kernel_size=(7,7), strides=(2,2), padding='SAME')(input)
        x = layers.Activation('relu')(x)
        x = layers.MaxPooling2D(pool_size=2)(x) #TODO make sure that pool_size is the same as kernal_size

        x = block_layers(nblocks, [fmaps[0],fmaps[0]])(x)
        x = block_layers(1, [fmaps[0],fmaps[1]])(x)
        x = block_layers(nblocks, [fmaps[1],fmaps[1]])(x)

        #TODO get pool size
        x = layers.MaxPooling2D()(x)
        x = layers.Flatten()(x)
        predictions = layers.Dense(1)(x)

        model = keras.Model(inputs=input, outputs=predictions)
        return model

