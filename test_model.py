import numpy as np
import tnse_plot
import pandas as pd
import torch
import ds
from torch.utils.data import DataLoader
from texttable import Texttable
import argparse

def getTable(t1,t3,t5,t10, total):
    t1_hit_ratio = format((t1['hit']/total*100),'.2f')
    t1_miss_ratio = format((t1['miss']/total*100),'.2f')
    t3_hit_ratio = format((t3['hit']/total*100),'.2f')
    t3_miss_ratio = format((t3['miss']/total*100),'.2f')
    t5_hit_ratio = format((t5['hit']/total*100),'.2f')
    t5_miss_ratio = format((t5['miss']/total*100),'.2f')
    t10_hit_ratio = format((t10['hit']/total*100),'.2f')
    t10_miss_ratio = format((t10['miss']/total*100),'.2f')

    table = Texttable()
    table.add_row(['T#','Hit', 'Miss', 'Hit %', 'Miss %','total'])
    table.add_row(['T1', t1['hit'], t1['miss'],t1_hit_ratio, t1_miss_ratio, total])
    table.add_row(['T3', t3['hit'], t3['miss'], t3_hit_ratio, t3_miss_ratio, total])
    table.add_row(['T5', t5['hit'], t5['miss'], t5_hit_ratio, t5_miss_ratio, total])
    table.add_row(['T10', t10['hit'], t10['miss'], t10_hit_ratio, t10_miss_ratio, total])
    return table.draw()


def test(path, device, is_printed):

    model_file = path + '/best_model.pt'
    test_file = path + '/test.csv'

    model = torch.load(model_file, map_location=torch.device('cpu')).to(device)
    model.eval()
    
    test = pd.read_csv(test_file, sep=";")
    test.columns = ['idx','code', 'phrase', 'phrases_length',
                    'class', 'encoded']

    ## PreModell
    X_test = list(test['encoded'])
    Y_test = list(test['class'])

    X_test_casted = list()
    for x in X_test:
        X_test_casted.append(np.array([int(s) for s in x.strip('[]').split() if s.isdigit()]))

    test_ds = ds.data(X_test_casted, Y_test)


    ## DataLoader
    batch_size = 1
    test_dl = DataLoader(test_ds, batch_size=batch_size)

    t1_dict = {'hit':0, 'miss':0}
    t3_dict = {'hit':0, 'miss':0}
    t5_dict = {'hit':0, 'miss':0}
    t10_dict = {'hit':0, 'miss':0}

    i = 0
    with torch.no_grad():
        for x, y, x_len in test_dl:
            i+=1
            x = x.long().to(device)
            y_pred = model(x,x_len)

            # Top 5 Predictions
            t1 = torch.topk(y_pred, 1)
            t3 = torch.topk(y_pred, 3)
            t5 = torch.topk(y_pred, 5)
            t10 = torch.topk(y_pred, 10)

            # Count if the code is within the T3 or not
            if y.item() in t1[1][0].numpy():
                t1_dict['hit'] = t1_dict['hit'] + 1
            else:
                t1_dict['miss'] = t1_dict['miss'] + 1

            # Count if the code is within the T3 or not
            if y.item() in t3[1][0].numpy():
                t3_dict['hit'] = t3_dict['hit'] + 1
            else:
                t3_dict['miss'] = t3_dict['miss'] + 1

            # Count if the code is within the T5 or not
            if y.item() in t5[1][0].numpy():
                t5_dict['hit'] = t5_dict['hit'] + 1
            else:
                t5_dict['miss'] = t5_dict['miss'] + 1

            # Count if the code is within the T3 or not
            if y.item() in t10[1][0].numpy():
                t10_dict['hit'] = t10_dict['hit'] + 1
            else:
                t10_dict['miss'] = t10_dict['miss'] + 1

    table = getTable(t1_dict,t3_dict,t5_dict,t10_dict,len(test))

    if is_printed:
        print(str(model_file))
        print(getTable(t1_dict,t3_dict,t5_dict,t10_dict,len(test)))

    with open(f'{path}/eval.txt', "w") as test_file:
        test_file.write(table)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process')
    parser.add_argument('--path', type=str, required=True)
    parser.add_argument('--device', default='cpu', type=str)
    parser.add_argument('--print', default= True)
    args = parser.parse_args()
    test(args.path, args.device, args.print)
