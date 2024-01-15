import textgrids
import cmudict_processing
import xlsxwriter

landmarks_to_phonemes = {'V': {'aa', 'ao', 'ow', 'ae', 'ax', 'ah', 'eh', 'ey', 'ih', 'iy', 'uh', 'uw', 'er', 'oy', 'ay', 'aw',
                                'aa0', 'ao0', 'ow0', 'ae0', 'ax0', 'ah0', 'eh0', 'ey0', 'ih0', 'iy0', 'uh0', 'uw0', 'er0', 'oy0','ay0','aw0'},
                         'V1':{'aa1', 'ao1', 'ow1', 'ae1', 'ax1', 'ah1', 'eh1', 'ey1', 'ih1', 'iy1', 'uh1', 'uw1', 'er1', 'oy1','ay1','aw1'},
                         'V2':{'aa2', 'ao2', 'ow2', 'ae2', 'ax2', 'ah2', 'eh2', 'ey2', 'ih2', 'iy2', 'uh2', 'uw2', 'er2', 'oy2','ay2','aw2'},
                         'G': {'w', 'y', 'l', 'r', 'h'},
                         'N': {'m', 'n', 'ng'},
                         'F': {'v', 'f', 'dh', 'th', 'z', 's', 'zh', 'sh'},
                         'S': {'b', 'p', 'd', 't', 'g', 'k'},
                         'A': {'jh', 'ch'}}     

landmarks_to_labels = {'V': ['V'],
                       'V1': ['V'],
                       'V2': ['V'],
                       'G': ['G'],
                       'N': ['Nc', 'Nr'],
                       'F': ['Fc', 'Fr'],
                       'S': ['Sc', 'Sr'],
                       'A': ['Sc', 'Sr', 'Fc', 'Fr']}

class Phoneme: 
    def __init__(self, phoneme, predLM = [], realLM = []):
        self.phoneme = phoneme.text.transcode() #str
        self.predLM = predLM # list of tuples --> [(predLM, timestamp)] 
        self.realLM = realLM # list of tuples --> [(realLM, timestamp)]
        self.realtime = None
        self.labels = None
        self.gen_lm = None
        self.context = None
        self.gen_context = None
        self.production = {'prev':None, 'cur':None, 'fol':None}
    def __repr__(self):
        return self.phoneme
    def is_vowel(self):
        return True if self.predLM[0][0] == 'V' else False
    def get_predLM(self):
        predlm = [plm[0] for plm in self.predLM]
        return predlm
    def get_realLM(self):
        reallm = [rlm[0] for rlm in self.realLM]
        return reallm
    def update_labels(self, labels):
        self.labels = labels
    def get_labels(self):
        labels = [label.text for label in self.labels]
        return labels
    def update_realtime(self,time):
        self.realtime = time
    def update_gen_lm(self, gen_lm):
        self.gen_lm = gen_lm
    def update_context(self,context):
        self.context = context
    def update_gen_context(self,gen_context):
        self.gen_context = gen_context
    def update_production(self,prev, cur, fol):
        self.production['prev'] = prev
        self.production['cur'] = cur
        self.production['fol'] = fol
        
    
class Word:
    def __init__(self, word, phonemes, accents):
        self.word = word.text.transcode()
        self.phonemes = phonemes # list of phoneme objects
        self.accents = accents
        self.breaks = ['', '']
        self.bound_tones = ['', '']
        self.matched_accents = {}
        try:
            self.stress = cmudict_processing.stress_dict[self.word]
        except KeyError:
            self.stress = f'Stress unavailable, "{self.word}" not found in dictionary' # make this a return statement??
        try:
            self.syllables = cmudict_processing.syllable_dict[self.word]
        except KeyError:
            # self.syllables = cmudict_processing.syllable_dict[self.word]
            pass
    def __repr__(self):
        return self.word
    def pred_time(self):
        start = self.phonemes[0].predLM[0][1] # xmin of first predLM of first phoneme
        end = self.phonemes[-1].predLM[-1][1] # xmax of last predLM of last phoneme
        return [start, end]
    def real_time(self):
        start = self.phonemes[0].realLM[0][1] # xmin of first realLM of first phoneme
        end = self.phonemes[-1].realLM[-1][1] # xmax of last realLM of last phoneme
        return [start, end]
    def match_accents(self, margin):
        for phoneme in self.phonemes:
            for acc in self.accents:
                if phoneme.realLM[0][1] - margin <= acc.xpos <= phoneme.realLM[-1][1] + margin:
                    self.matched_accents[phoneme] = (acc.text.transcode(), acc.xpos) # want this to be phoneme or phoneme.phoneme?
    def update_pre_breaks(self, preceding_break):
        self.breaks[0] = preceding_break
    def update_fol_breaks(self, following_break):
        self.breaks[1] = following_break
    def update_pre_bound_tones(self, preceding_tone):
        self.bound_tones[0] = preceding_tone
    def update_fol_bound_tones(self, following_tone):
        self.bound_tones[1] = following_tone



class Phrase:
    def __init__(self, words, bound_tones, breaks):
        self.words = words # list of word objects
        self.bound_tones = bound_tones
        self.breaks = breaks
        self.matched_bound_tones = {}
        self.matched_breaks = {}
    def __repr__(self):
        phrase = " ".join([word.word for word in self.words])
    def match_tones(self, margin): # improve efficiency
        for tone in self.bound_tones:
            for i in range(len(self.words)):
                if i != len(self.words) - 1:
                    if self.words[i].real_time()[1] - margin <= tone.xpos <= self.words[i+1].real_time()[0] + margin:
                        self.matched_bound_tones[(self.words[i], self.words[i+1])] = (tone.text.transcode(), tone.xpos)
                        self.words[i].update_fol_bound_tones(tone.text.transcode())
                        self.words[i+1].update_pre_bound_tones(tone.text.transcode())
                        break 

                else:
                    if self.words[i].real_time()[1] - margin <= tone.xpos <= self.words[i].real_time()[1] + margin:
                        self.matched_bound_tones[(self.words[i],)] = (tone.text.transcode(), tone.xpos)
                        self.words[i].update_fol_bound_tones(tone.text.transcode())

    def match_breaks(self, margin): # improve efficiency
        for br in self.breaks:
            for i in range(len(self.words)):
                if i != len(self.words) - 1:
                    if self.words[i].real_time()[1] - margin <= br.xpos <= self.words[i+1].real_time()[0] + margin:
                        self.matched_breaks[(self.words[i], self.words[i+1])] = (br.text.transcode(), br.xpos)
                        self.words[i].update_fol_breaks(br.text.transcode())
                        self.words[i+1].update_pre_breaks(br.text.transcode())
                        break
                else:
                    if self.words[i].real_time()[1] - margin <= br.xpos <= self.words[i].real_time()[1] + margin:
                        self.matched_breaks[(self.words[i],)] = (br.text.transcode(), br.xpos)
                        self.words[i].update_fol_breaks(br.text.transcode())

    def get_phrase(self):
        phrase = ''
        for word in self.words:
            phrase += word.word
            phrase += ' '
        return phrase

def get_predicted_labels(phoneme):
    for landmark in landmarks_to_phonemes:
        if phoneme in landmarks_to_phonemes[landmark]:
            return landmarks_to_labels[landmark]
            
            
def make_phonemes(lexi):
    """
    params: 
        lexi: a LEXI TextGrid post alignment algorithm
        tobi: a ToBI TextGrid
    returns:
        a list of Phoneme objects
    """
    phonemes = [ph for ph in lexi['phonemes'] if ph.text.transcode() != ''] 
    all_predlms = [lm for lm in lexi['predLM']]
    all_reallms = [lm for lm in lexi['allRealizedLM']]
    all_alignedlms = [lm for lm in lexi['alignedLM']]
    phoneme_objects = []
   
    # make phoneme objects

    for ph in phonemes:
        plm = []
        predLM = []
        rlm = []
        realLM = []
        temp = []
        #get predicted landmarks for a phoneme
        for landmark in landmarks_to_phonemes:
            if ph.text.transcode() in landmarks_to_phonemes[landmark]:
                plm.extend(landmarks_to_labels[landmark])
                
        #get the actual landmark objects for the phoneme by popping
        #the 1st element of predlms n times, where n = length of plm
     
        for i in range(len(plm)):
            pred = all_predlms[0]
            # pred = all_predlms.pop(0)
            if pred.text.transcode() == plm[i]:
                pred = all_predlms.pop(0)
                predLM.append((pred.text.transcode(),pred.xpos))
       


        if len(predLM) != len(plm):
            continue
        #get realized landmarks for a phoneme(includes modifications)
        #edit this so that it doesn't need to loop through all of alignedlms
        for i in predLM:
            for j in all_alignedlms:
                if abs(i[1]-j[1]) <= .0005: #these numbers are arbitrary, edit them
                    rlm.append(j)
        # print(ph.text.transcode(),rlm)
    

        #now that we know what the realized lms are, get their actual timestamps
        count = len(rlm)
        for i in rlm:
            for j in range(len(all_reallms)):
                if i.text.transcode() == all_reallms[j].text.transcode() and count != 0:
                    temp = all_reallms.pop(j)
                    realLM.append((temp.text.transcode(),temp.xpos,temp))
                    count -= 1
                    break


        phoneme_objects.append(Phoneme(ph, predLM, realLM))     

    
    # update real times

    for i in range(len(phoneme_objects)):
        # need to edit to make more succint, realtimes have different lengths rn
        pred_labels = get_predicted_labels(phoneme_objects[i].phoneme)
        
        if len(pred_labels) != 1: # if not "V" or "G"
            phoneme_objects[i].realtime = [x[1] for x in phoneme_objects[i].realLM]
            # print(phoneme_objects[i].phoneme,phoneme_objects[i].realtime,phoneme_objects[i].realLM)

        else:
            # might need to include try/except here if time is out of bounds
            if i == 0: # if first phoneme
                phoneme_objects[i].realtime = [phoneme_objects[i].realLM[0][-1].xpos-.1,phoneme_objects[i+1].realLM[0][-1].xpos]
                
            elif i == len(phoneme_objects) - 1: # if last phoneme
                phoneme_objects[i].realtime = [phoneme_objects[i-1].realLM[-1][-1].xpos, phoneme_objects[i].realLM[-1][-1].xpos+.1]
            else:
                # print(phoneme_objects[i].phoneme,phoneme_objects[i].realLM)
                # print(phoneme_objects[i+1].phoneme,phoneme_objects[i+1].realLM)
                phoneme_objects[i].realtime = [phoneme_objects[i-1].realLM[-1][-1].xpos, phoneme_objects[i+1].realLM[-1][-1].xpos]
   
  

    labels = [() for i in range(len(phonemes))]
    vgplace = list(lexi['vgplace'])
    cplace = list(lexi['cplace'])
    nasal = list(lexi['nasal'])
    glottal = list(lexi['glottal'])
    all_labels = sorted(vgplace + cplace + nasal + glottal, key=lambda p: p.xpos)
    # i = 0

    for i in range(len(phoneme_objects)):
        for label in all_labels:
            # print(phoneme_objects[i].realtime[0], label.xpos, phoneme_objects[i].realtime[-1])
            if phoneme_objects[i].realtime[0] <= label.xpos <= phoneme_objects[i].realtime[-1]:
                labels[i] += (label, )
                # print(phoneme_objects[i],labels[i])
        
    
             

        #     i += 1
        # i = 0
    
    for phoneme,label in zip(phoneme_objects, labels):
        # print(phoneme.phoneme,label)
        phoneme.update_labels(label)
        # print(phoneme.phoneme, phoneme.realtime, phoneme.get_labels())
    

    for landmark in landmarks_to_phonemes:
        for ph in phoneme_objects:
            if ph.phoneme in landmarks_to_phonemes[landmark]:
                ph.update_gen_lm(landmark)
             

    
    for i in range(len(phoneme_objects)):
        if i == 0:
            prev = None
            cur = phoneme_objects[i]
            fol = phoneme_objects[i+1]
            phoneme_objects[i].update_context((prev,cur.phoneme,fol))
            phoneme_objects[i].update_gen_context((prev,cur.phoneme,fol.gen_lm))
            phoneme_objects[i].update_production(prev,cur.get_realLM(),fol.get_realLM()[0])
            
        elif i == len(phoneme_objects)-1:
            prev = phoneme_objects[i-1]
            cur = phoneme_objects[i]
            fol = None
            phoneme_objects[i].update_context((prev,cur.phoneme,fol))
            phoneme_objects[i].update_gen_context((prev.gen_lm,cur.phoneme,fol))
            phoneme_objects[i].update_production(prev.get_realLM()[-1],cur.get_realLM(),fol)
        else:
     
            prev = phoneme_objects[i-1]
            cur = phoneme_objects[i]
            fol = phoneme_objects[i+1]
            phoneme_objects[i].update_context((prev,cur,fol))
            phoneme_objects[i].update_gen_context((prev.gen_lm,cur.phoneme,fol.gen_lm))
            phoneme_objects[i].update_production(prev.get_realLM()[-1],cur.get_realLM(),fol.get_realLM()[0])
        
    return phoneme_objects


def make_words(lexi, tobi, phoneme_objects):
    # currently assumes lexi and tobi words tier are identical
    if tobi == None:
        words = [word for word in lexi['words'] if "<" not in word.text.transcode()]
        phonemes = [ph for ph in lexi['phonemes'] if ph.text.transcode() != '']
       
        word_objects = []
        start = 0
        end = 0
        for word in words:
            for phoneme in phonemes:
                if word.xmin <= phoneme.mid <= word.xmax:
                    end += 1
            
            if len(phoneme_objects[start:end]) == 0:
                continue

            word_objects.append(Word(word, phoneme_objects[start:end],None))
            start = end
        return word_objects
    else:
        words = [word for word in lexi['words'] if "<" not in word.text.transcode()]
        phonemes = [ph for ph in lexi['phonemes'] if ph.text.transcode() != '']
        accents = [acc for acc in tobi['tones'] if "*" in acc.text.transcode()]
        word_objects = []
        start = 0
        end = 0
        for word in words:
            for phoneme in phonemes:
                if word.xmin <= phoneme.mid <= word.xmax:
                    end += 1
            
            if len(phoneme_objects[start:end]) == 0:
                continue

            word_objects.append(Word(word, phoneme_objects[start:end],accents))
            start = end
        
        for word in word_objects:
            word.match_accents(.03)

        return word_objects

def make_phrase(lexi, tobi, word_objects):
    if tobi == None:
        phrase_object = Phrase(word_objects, None, None)
        return phrase_object
    else:
        boundary_tones = [tone for tone in tobi['tones'] if "*" not in tone.text.transcode()]
        breaks = [br for br in tobi['breaks']]
        phrase_object = Phrase(word_objects, boundary_tones, breaks)
        phrase_object.match_tones(.03)
        phrase_object.match_breaks(.03)
        return phrase_object        


def run(lexi,tobi):
    """
    params: lexi- LEXI TextGrid after alignment algorithm has been run
            tobi- ToBI TextGrid
    relies on christine's algorithm being correct
    """
    phonemes = make_phonemes(lexi)
    words = make_words(lexi, tobi, phonemes)
    phrase = make_phrase(lexi, tobi, words)




if __name__ == '__main__':     
    pass
    # lexi_tg = textgrids.TextGrid('test_textgrids/conv01_pt1/conv01_Suyeon_checked_SC_EW_pt1_gen_alig.TextGrid')
    # tobi_tg = textgrids.TextGrid('test_textgrids/conv01_pt1/conv01g_ahl_ToBI_pt1.TextGrid')
    # run(lexi_tg, tobi_tg,'test_output_kate.xlsx')

    # lexi_tg = textgrids.TextGrid('/Users/sofiechung/SuperUROP/BettyBought/BettyBought_choi_edits_2-24-23_alig.TextGrid')
    # tobi_tg = textgrids.TextGrid('/Users/sofiechung/SuperUROP/BettyBought/BettyBought_ToBI ssh.TextGrid')
    # run(lexi_tg, tobi_tg)

    lexi_tg = textgrids.TextGrid('/Users/sofiechung/SuperUROP/todo/DR1/FCJF0/SX217.TextGrid')
    run(lexi_tg,None)

