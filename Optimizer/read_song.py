
import librosa

x, sr = librosa.load('../Audios Fernan/regueton-ciclico-medio-malito.ogg')       

onset_frames = librosa.onset.onset_detect(x, sr=sr, wait=1, pre_avg=1, post_avg=1, pre_max=1, post_max=1)
onset_times = list(librosa.frames_to_time(onset_frames))

print(onset_times)

