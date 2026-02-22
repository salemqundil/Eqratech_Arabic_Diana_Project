from phonemes_engine import PhonemesEngine
import pandas as pd


def compare():
    phon_df = PhonemesEngine.make_df()
    csv_df = pd.read_csv('full_multilayer_grammar.csv', dtype=str).fillna('')
    try:
        xlsx_df = pd.read_excel('full_multilayer_grammar.xlsx', sheet_name='الفونيمات')
    except Exception as e:
        xlsx_df = None

    print('engine rows:', len(phon_df))
    print('csv rows   :', len(csv_df))
    if xlsx_df is not None:
        print('xlsx rows  :', len(xlsx_df))

    eng_list = phon_df['الفونيمات'].astype(str).tolist()
    csv_list = csv_df['الفونيمات'].astype(str).tolist()

    same = eng_list == csv_list
    print('\nlists identical:', same)

    if not same:
        # show first mismatch
        for i, (e, c) in enumerate(zip(eng_list, csv_list)):
            if e != c:
                print(f'first mismatch at index {i}: engine="{e}", csv="{c}"')
                break

    # show sample previews
    print('\nengine sample:')
    print(phon_df.head(10).to_string(index=False))
    print('\ncsv sample:')
    print(csv_df.head(10).to_string(index=False))


if __name__ == '__main__':
    compare()
