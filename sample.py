# coding: utf-8

'''
得到某个视频的caption和attention vector
'''

from __future__ import unicode_literals
from __future__ import absolute_import
import cv2
from caption import Vocabulary
from model import BANet
from args import video_root, video_sort_lambda
from args import vocab_pkl_path, feature_h5_path, feature_h5_feats
from args import best_banet_pth_path
from args import feature_size, max_frames, max_words
from args import projected_size, hidden_size, mid_size
from args import use_cuda
from args import visual_dir
import os
import sys
import pickle
import torch
import h5py
import numpy as np


def open_video(video_path):
    try:
        cap = cv2.VideoCapture(video_path)
    except:
        print('Can not open %s.' % video_path)
        pass

    frame_list = []
    frame_count = 0
    while True:
        ret, frame = cap.read()
        if ret is False:
            break
        # cv2.imshow('Video', frame)
        # cv2.waitKey(30)
        frame_list.append(frame)
        frame_count += 1
    indices = np.linspace(0, frame_count, max_frames, endpoint=False, dtype=int)
    frame_list = np.array(frame_list)[indices]
    return frame_list


def sample(vocab, video_feat, banet, video_path, vid):
    # 为每个视频建立保存可视化结果的目录
    img_dir = os.path.join(visual_dir, str(vid))
    if not os.path.exists(img_dir):
        os.mkdir(img_dir)

    # frame_list = open_video(video_path)
    if use_cuda:
        video_feat = video_feat.cuda()
    video_feat = video_feat.unsqueeze(0)
    outputs, video_encoded = banet(video_feat, None)
    words = []
    for i, token in enumerate(outputs.data.squeeze()):
        if token == vocab('<end>'):
            break
        word = vocab.idx2word[token]
        # print(word)
        words.append(word)
    caption = ' '.join(words)
    print(caption)


if __name__ == '__main__':
    with open(vocab_pkl_path, 'rb') as f:
        vocab = pickle.load(f)

    features = h5py.File(feature_h5_path, 'r')[feature_h5_feats]

    # 载入预训练模型
    banet = BANet(feature_size, projected_size, mid_size, hidden_size,
                  max_frames, max_words, vocab)
    banet.load_state_dict(torch.load(best_banet_pth_path))
    banet.cuda()
    banet.eval()

    videos = sorted(os.listdir(video_root), key=video_sort_lambda)

    if len(sys.argv) > 1:
        vid = int(sys.argv[1])
        video_path = os.path.join(video_root, videos[vid])
        video_feat = torch.autograd.Variable(torch.from_numpy(features[vid]))
        sample(vocab, video_feat, banet, video_path, vid)
    else:
        # selected_videos = [1412, 1420, 1425, 1466, 1484, 1554, 1821, 1830, 1841,
        #                    1848, 1849, 1850, 1882, 1884, 1931, 1934, 1937, 1944,
        #                    1949, 1950, 1951, 1962]
        # for vid in selected_videos:
        for vid in range(100):
            print(vid)
            video_path = os.path.join(video_root, videos[vid])
            video_feat = torch.autograd.Variable(torch.from_numpy(features[vid]))
            sample(vocab, video_feat, banet, video_path, vid)
