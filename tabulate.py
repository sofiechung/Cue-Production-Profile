import speech_ds
import textgrids
import os
import pandas as pd

def context_filter(phoneme, contexts):
    filtered = []
    for c in contexts: 
      
        if c[1] == phoneme:
            filtered.append(c)
    # print(filtered)
    return filtered

# def context_filter(targets, contexts):
#     """
#     @params
#         targets: a set of 3-element tuples- (general LM, phoneme, general LM)
#         contexts: a list of 3-element tuples that contain the contexts we want to filter through
#     """
#     filtered = []
#     tabulate = {}
#     i = 0
#     for c in contexts:
#         tabulate[c] = 0
#     for c in contexts:
#         if targets=='all' or c in targets:
#             filtered.append(c)
#             tabulate[c] += 1
#     return filtered, tabulate




def productions(target,phoneme_objects):
    output = []
    for ph in phoneme_objects:
        if ph.phoneme == target:
            output.append(ph.production)
    return output

def tabulate(phonemes, filtered_contexts):
    tabulations = {}
    for c in filtered_contexts:
        if c not in set(tabulations.keys()):
            tabulations[c] = {'count':1}
        else:
            tabulations[c]['count'] += 1
    for phoneme in phonemes:
        if phoneme.gen_context in set(tabulations.keys()):
            for realLM in phoneme.realLM:
                if realLM[0] not in set(tabulations[phoneme.gen_context].keys()): 
                    tabulations[phoneme.gen_context][realLM[0]] = 1
                else:
                    tabulations[phoneme.gen_context][realLM[0]] += 1
            labels = phoneme.get_labels()
        
            for label in labels:
                if label not in set(tabulations[phoneme.gen_context].keys()):
                    tabulations[phoneme.gen_context][label] = 1
                else:
                    tabulations[phoneme.gen_context][label] += 1
    return tabulations

def tabulate_v1(phonemes, filtered_contexts):
    tabulations = {}
   
    for c in filtered_contexts:
        if c not in set(tabulations.keys()):
            tabulations[c] = []
        # else:
        #     tabulations[c][0] += 1
    for phoneme in phonemes:
        temp = []
        # print(phoneme.gen_context)
        if phoneme.gen_context in set(tabulations.keys()):
            
            for realLM in phoneme.realLM:
                temp.append(realLM[0])
            # labels = phoneme.get_labels()
            # temp.extend(labels)
            tabulations[phoneme.gen_context].append(temp)
        
    return tabulations

def combine_all_tabulations_v1(tabulations):
    final_tabulations = {}
    for tabulation in tabulations:
        for context in tabulation:
            if context not in final_tabulations:
                final_tabulations[context] = tabulation[context]
            else:
                final_tabulations[context].extend(tabulation[context])
    return final_tabulations

def combine_all_tabulations(tabulations):
    final_tabulations = {}
    for tabulation in tabulations:
        for context in tabulation:
            if context not in final_tabulations:
                final_tabulations[context] = tabulation[context]
            else:
                for label in tabulation[context]:
                    if label in final_tabulations[context]:
                        final_tabulations[context][label] += tabulation[context][label]
                    else:
                        final_tabulations[context][label] = tabulation[context][label]
    
    return final_tabulations

def is_textgrid(path_to_file):
    '''
    Checks to see if path_to_file is a TexGrid file.

    @param path_to_file a string path
    @return true if the path_to_file points to a TextGrid file, false otherwise
    '''
    return path_to_file.lower().endswith('.textgrid')

def get_all_textgrids_from_directory(path_to_directory):
    '''
    Get a list of valid Textgrids from a directory.

    @param path_to_directory a string path (relative or absolute) to the directory of interest
    @return a list of all the paths to the TextGrid files in the directory
    '''
    all_paths = []
    if is_textgrid(path_to_directory):
        all_paths.append(path_to_directory)
        

    else:
        for (dirpath, _, filenames) in os.walk(path_to_directory):
            for filename in filenames:
                if is_textgrid(filename):
                    all_paths.append(dirpath + '/' + filename)
    return all_paths

def runv1(all_textgrid_paths):
    tabulations = []
    columns = ['context', 'production', 'type']
    data = []
    rows = []
    for textgrid_path in all_textgrid_paths:
        textgrid = textgrids.TextGrid(textgrid_path)
        filename = textgrid_path[33:-9] #fix
        phonemes = speech_ds.make_phonemes(textgrid)
        words = speech_ds.make_words(textgrid, None, phonemes)
        phrase = speech_ds.make_phrase(textgrid, None, words)
        contexts = []
        for phoneme in phonemes:
            contexts.append(phoneme.gen_context)
        filtered = context_filter('t', contexts)
        textgrid_tabulation = tabulate_v1(phonemes, filtered)
        count = 0
        for context in textgrid_tabulation:
            for prod in textgrid_tabulation[context]:
                temp = [context]
                temp.append(prod)
                # default 
                if prod == ['Sc','Sr']:
                    temp.append('Default')
                elif context == ('V','t','V') and 'G-+' in set(prod):
                    temp.append('Flapping')
                elif prod == ['Sc','Sr-x']:
                    temp.append('Unreleased')
                else:
                    temp.append('-')
                data.append(temp)
                count += 1
                
        new_rows = [filename] * count
        rows.extend(new_rows)


    df = pd.DataFrame(data, index = rows, columns = columns)
    return df

    


# def run(all_textgrid_paths):
#     tabulations = []
#     output = ""

#     for textgrid_path in all_textgrid_paths:
#         print("Currently tabulating: " + textgrid_path)
#         output += "\n" + textgrid_path + "\n"
#         textgrid = textgrids.TextGrid(textgrid_path)
#         phonemes = speech_ds.make_phonemes(textgrid)
#         words = speech_ds.make_words(textgrid, None, phonemes)
#         phrase = speech_ds.make_phrase(textgrid, None, words)
#         contexts = []
     
#         for phoneme in phonemes:
#             contexts.append(phoneme.gen_context)
#         filtered = context_filter('t',contexts)
#         textgrid_tabulation = tabulate_v1(phonemes, filtered)
#         # print(textgrid_tabulation)
#         tabulations.append(textgrid_tabulation)

#     final_tabulations = combine_all_tabulations_v1(tabulations)
    
#     return final_tabulations, output


# def run(lexi,tobi):
#     """
#     params: lexi- LEXI TextGrid after alignment algorithm has been run
#             tobi- ToBI TextGrid
#     relies on christine's algorithm being correct
#     """
#     phonemes = speech_ds.make_phonemes(lexi)
#     words = speech_ds.make_words(lexi, tobi, phonemes)
#     phrase = speech_ds.make_phrase(lexi, tobi, words)
#     contexts = []
#     for phoneme in phonemes:
#         contexts.append(phoneme.gen_context)
#     filtered = context_filter('b',contexts)
#     tabulations = tabulate(phonemes, filtered)
#     print(tabulations)

if __name__ == '__main__':
    # all_textgrids = get_all_textgrids_from_directory('/Users/sofiechung/SuperUROP/BettyBought/BettyBought_choi_edits_2-24-23_alig.TextGrid')
    paths = ["/Users/sofiechung/SuperUROP/todo/DR1/FCJF0",
             "/Users/sofiechung/SuperUROP/todo/DR1/MCPM0",
             "/Users/sofiechung/SuperUROP/todo/DR2/FAEM0",
             "/Users/sofiechung/SuperUROP/todo/DR2/MARC0",
             "/Users/sofiechung/SuperUROP/todo/DR3/FALK0",
             "/Users/sofiechung/SuperUROP/todo/DR3/MADC0",
             "/Users/sofiechung/SuperUROP/todo/DR4/FALR0",
             "/Users/sofiechung/SuperUROP/todo/DR4/MAEB0",
             "/Users/sofiechung/SuperUROP/todo/DR5/FBJL0",
             "/Users/sofiechung/SuperUROP/todo/DR5/MGBT0",
             "/Users/sofiechung/SuperUROP/todo/DR6/FAPB0",
             "/Users/sofiechung/SuperUROP/todo/DR6/MABC0",
             "/Users/sofiechung/SuperUROP/todo/DR7/FBLV0",
             "/Users/sofiechung/SuperUROP/todo/DR7/MADD0",
             "/Users/sofiechung/SuperUROP/todo/DR8/FBCG1",
             "/Users/sofiechung/SuperUROP/todo/DR8/MBCG0"]
 
    # path_to_directory = input("What is the path to your directory: ")

    # all_textgrid_paths = get_all_textgrids_from_directory(path_to_directory)
    all_textgrid_paths = []
    for p in paths:
        all_textgrid_paths.extend(get_all_textgrids_from_directory(p))
    
    # final_tabulations = run(all_textgrid_paths)



    # while not all_textgrid_paths:
    #     print("There are no textgrid files here. Did you mistype the path?")
    #     path_to_directory = input("What is the path to your directory: ")
    #     all_textgrid_paths = get_all_textgrids_from_directory(path_to_directory)

    # final_tabulations, output = run(all_textgrid_paths)
    
    final = runv1(all_textgrid_paths)
    # final_excel = final.to_excel("contexts.xlsx")  

    # print(final)
    # speakers = []
    # index = list(final.index)
    # temp = index[0][4:9]
    # unique_speakers = set()
    # for speaker in index:
    #     unique_speakers.add(speaker[4:9])
    
    # temp = []
    # for speaker in unique_speakers:
    #     temp 

    # speakers =  []
    # # print(final.index)
    # index = list(final.index)
    # temp = index[0][4:9]
    # speaker_subset = set()
    # for speaker in index:
    #         if speaker[4:9] == temp:
    #             speaker_subset.add(speaker)
    #         else:
    #             speakers.append(list(speaker_subset))
    #             speaker_subset = set()
    #             temp = speaker[4:9]
    #             speaker_subset.add(speaker)
    # speakers.append(list(speaker_subset))

    # print(speakers, len(speakers))
    # for speaker in speakers:
    #     for sentence in speaker:
    #         final.loc[speaker[4:9], 'label' == 'flapping'].sum()


    # for speaker in speakers:
    #     temp = []
    #     df
    #     df.loc[df['a'] == 1, 'b'].sum()
        
    
            # df.loc[df['a'] == 1, 'b'].sum()

    # print(final_tabulations)
    # output_file_name = path_to_directory.split('/')[-1] + "_output.txt"
    # output_file = open(output_file_name, 'w+')
    # output_file.write(output)
    # output_file.write("\nSummary\n")
    # output_file.write(str(final_tabulations))
    # output_file.close()