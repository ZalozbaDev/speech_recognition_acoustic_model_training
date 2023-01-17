from audiomentations import SomeOf, AddGaussianNoise, TimeStretch, PitchShift, Shift, AddBackgroundNoise, PolarityInversion, RoomSimulator
import numpy as np
import sys
from scipy.io import wavfile
import glob, os


augument = SomeOf((1, 3), [
    AddGaussianNoise(min_amplitude=0.001, max_amplitude=0.015, p=0.5),
    TimeStretch(min_rate=0.9, max_rate=1.1, p=0.5),
    PitchShift(min_semitones=-4, max_semitones=4, p=0.5),
    # Shift(min_fraction=-0.5, max_fraction=0.5, p=0.5),
    AddBackgroundNoise(sounds_path="noise", min_snr_in_db=3.0, max_snr_in_db=30.0,noise_transform=PolarityInversion(),p=1.0)
])



'''Main loop'''
if __name__ == "__main__":

    if len(sys.argv) < 3:
        print(f'Usage: {sys.argv[0]} inputfolder outputfolder')
        raise SystemExit()

    ''' 
        *   inputfolder    - folder where all wav files will be augmented
        *   outfile        - folder for the augmented files
    '''
 
    for f in glob.glob(sys.argv[1]+'/**/*.wav', recursive=True):
        samplerate, data = wavfile.read(f)
        augmented_samples = augument(samples=data.astype(np.float32), sample_rate=16000)
        ofile=f.replace(sys.argv[1],sys.argv[2])
        print(ofile)
        os.makedirs(os.path.dirname(ofile), exist_ok=True)
        wavfile.write(ofile, 16000, augmented_samples.astype(np.int16))
    
    print('end')