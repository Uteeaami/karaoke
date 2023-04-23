import srt
import enchant
global syllables
global to_be_removed
from datetime import timedelta

transcribed = open("vocals16k.wav.srt", encoding='utf8')
transcribed = list(srt.parse(transcribed))
lyrics = open("lyrics.txt", encoding='utf8')
lyrics = lyrics.read()

# whisper.cpp output with max-len = 1 by line gives bad output and sometimes slices
# words by syllables to the next subtitle (this data could be used to tempo the words
# if it was more accurate)

def wordbuilder():
    global syllables
    global to_be_removed
    syllables = []
    word_index = -1
    counter = 0
    banned_start = ['[', '(', '*', '\\']
    banned_end = ['*', ')', ']', '}']
    discard = ['♪']
    discard_string = [".txt"]
    temp_string = ""
    count = 0
    count2 = 0
    words = []
    flag = 1
    to_be_removed = []
    to_be_removed2 = []
    word_index = -1
    checker = 0

    for slice in transcribed:
        count += 1
        #print(transcribed[0])
        string = str(slice.content)
        temp_string += string
        
    # discard by string (len currently 3)
        
        if (count % 3 == 0):
            #print(temp_string)
            if (temp_string in discard_string):
                temp_string = ""
                flag = 1
                while (flag == 1):
                    count2 += 1
                    temp_string = str(transcribed[slice.index - count2].content)
                    #print(temp_string)
                    if (temp_string[0] == " "):
                        print("START")
                        print(slice.index - count2, slice.index)
                        for i in range(slice.index - count2, slice.index):
                            to_be_removed.append(i)
                        count2 = 0
                        flag = 0
                    
            temp_string = ""

    for slice in transcribed:
        count += 1
        #print(transcribed[0])
        string = str(slice.content)
        temp_string += string
    
   # discard subtitles by char                 
        for char in string:
            if(char in discard):
                to_be_removed.append(slice.index)



    # whisper sometimes transcribes non essential data, such as (music), *birds chirping*,
    # [jatkuu], this block removes transcribed indices between unwanted symbols as defined
    # in banned_start and end   
            if(char in banned_start):
                temp = []
                flag = 1
                checker = slice.index -1
                last = slice.index -1
                temp.append(checker + 1)
                while (flag == 1 and checker + 1 < len(transcribed)):
                    checker += 1
                    string2 = str(transcribed[checker].content)
                    #print(string2)
                    #print(checker + 1)
                    for char2 in string2:
                        #print(char2)
                        if(char2 in banned_end):
                            to_be_removed.append(checker + 1)
                            temp.append(checker + 1)
                            #print(temp)
                            if (len(temp) == 2):
                                for i in range(temp[0], temp[1]):
                                    #print(i)
                                    to_be_removed.append(i)
                            flag = 0
                            break

    # new words start with empty space in transcription " ", errors if line is empty
        counter = 0
        try:                
            if (slice.index in to_be_removed):
                print(string, "@ ", slice.index,  " not added, unwanted")
            # recognize new word
            elif(string[0] == " "):
                # removes the empty space
                word_index += 1
                words.append(string[1:len(string)])
                syllables.append(1)
            # append rest of syllables
            else:
                syllables[word_index] = syllables[word_index] + 1
                words[word_index] += string
        except Exception as e:
            print(string, "@ ", slice.index,  " not added, ", e)
            to_be_removed.append(slice.index)
        
    print(syllables)
    print(banned_start)
    print(banned_start)
    print(banned_start)
    print(banned_start)
    print(banned_start)
    print(len(syllables))
    print("indices of bogus lines ", to_be_removed)
    #print("debug: ", to_be_removed2)
    return words

# main

words = wordbuilder()
print(words)
print("number of words in transcribed: ", len(words))


#cleaned = list(srt.parse(cleaned))
#print(cleaned[0])
asd = ""

# create dictionary for enchant for spellcheck, input = original lyrics
# save it to a file to use as personal word list
for i in range(len(lyrics)):
    if (lyrics[i] == '\n'):
        asd += ' '
    else:
        asd += lyrics[i]
asd2 = ""
for i in range(len(asd)):
    if (asd[i] == ' '):
        asd2 += '\n'
    else:
        asd2 += lyrics[i]
with open ('dict.txt', 'w+', encoding="utf-8") as lyric:
    lyric.write(asd2)
lyric_dict = open("dict.txt", encoding='utf8')
lyric_dict = lyric_dict.readlines()


# enchant transcription for better matching to real lyrics
pwl = enchant.request_pwl_dict('dict.txt')
estimated = []
for word in words:
    # pwl.suggest returns a list of recommended words, can be empty!
    new = pwl.suggest(word)
    if(len(new) > 0):
        estimated.append(new[0])
    else:
        estimated.append(word)
    #print(pwl.suggest(word))
print(estimated)
print("number of words in enchanted lyrics ", len(estimated))

lyrics = open("lyrics.txt", encoding='utf8')
lyrics = lyrics.readlines()
for line in lyrics:
    print(line)
print("number of words in real lyrics: ", len(lyric_dict))
#print(asd2)

# create list of actual subs (not bogus)
cleaned = []
for slice in transcribed: # was transcribed
    if(slice.index not in to_be_removed):
        cleaned.append(slice)


# get perfet lyric matches between estimated and real
perfects = []
ranges = []
missed = []
dups = []
word_counts = []
count = -1

print(estimated)
# this block needs to know/find out/fuck around the indices of original subs for anything to make sense (no)
for line in lyrics:
    count += 1
    word_count = 1      # last word has no space = 0 + 1
    for char in line:
        if (char == " "):
            word_count += 1
    word_counts.append(word_count)
    # i = start index where to start finding slices
    for i in range(len(estimated) - word_count): # - word_count can cause an error since its from real lyrics
        string = ""
        # j = indices of estimated list
        for j in range(i, word_count + i):
            string += estimated[j]
            if (j != word_count + i - 1): # dont add space if last word of slice
                string += " "
        line2 = line.rstrip("\n")

        if (line2.casefold() == string.casefold()): # and j-word_count + 1 not in ranges), ranges are wrong for now if same line appear
                              # earlier in lyrics (common in music)
            if (j-word_count +1 in ranges and j in ranges): # add and count not in temp if you want temp to contain dubs that should work
                print(j-word_count +1, ", ", j)
                if (count in missed):
                    missed.remove(count)
                else:
                    #ranges.append(j-word_count + 1)
                    #ranges.append(j)
                    #perfects.append(count)
                    missed.append(count)
                #print(count)
                #perfects.append(count)
            else:
                ranges.append(j-word_count + 1)
                ranges.append(j)
                if (count not in perfects):
                    perfects.append(count) # adds two pairs if lines are identical, fix? below
                else:
                    cond = True
                    temp = count + 1
                    while (cond == True):
                        #print(lyrics[temp].casefold().rstrip("\n") == line2.casefold())
                        #print(line2)
                        #print(lyrics[temp])
                        if(lyrics[temp].casefold().rstrip("\n") == line2.casefold()):
                            dups.append(temp)
                            perfects.append(temp)
                            temp = 0
                            cond = False
                        temp += 1

print("missed but correct: ", missed)
print("duplicate available: ", dups)
#over_engineer = 0
#for i in range(len(perfects)-1):
#   if(perfects[i + 1] == perfects[i]):
#        over_engineer += 1
#        perfects[i+1] = '#'
#for times in range(over_engineer):
#    perfects.remove('#')

in_betweeners = []
for i in range(len(lyrics)):
    if (i not in perfects):
        if(i -1 in perfects and i +1 in perfects):
            in_betweeners.append(i)
            perfects.append(i)
        if(i -1 == -1 and i +1 in perfects):
            in_betweeners.append(i)
            perfects.append(i)
        if(i -1 in perfects and i +1 == len(lyrics)):
            in_betweeners.append(i)
            perfects.append(i)

perfects.sort()
print("perfect mathes: ", (perfects))
#print("duplicates; ", duplicates)
#print((word_counts))
print("inbetweeners: ", in_betweeners)
ranges.sort()
print("ranges: ", ranges)

# get max word count
word_count = 0
for i in range(len(word_counts)):
    word_count += word_counts[i]

# add inbetweeners, quaranteed to be proper
count = 0
index = 0
for i in range(len(perfects)):
    first = False
    last = False
    if (perfects[i] in in_betweeners):
        index = (2*(i-count)) - 1
        #print("index: ", index, "i: ", i, "count: ", count)
        #print(ranges[index])
        if (perfects[i] == len(lyrics) - 1):
            last = True
            ranges.append(ranges[index] + 1)
            ranges.append(word_count)
        if (perfects[i] == 0):
            first = True
            ranges.append(ranges[0] - 1)
            ranges.append(0)
        elif (first != True and last != True):
            ranges.append(ranges[index] + 1)
            ranges.append(ranges[index + 1] - 1)
        
        count += 1

ranges.sort()
print("ranges after inbetweeners: ", ranges)

# add lines by length, not quaranteed to be 100% true
flag = 0
count = 0
count2 = 0
count3 = 0
adder = 0
index = 0
lengths = []
temp = []
last_range = 0
for i in range(len(lyrics)):
    if (i not in perfects):
        count += 1
        print("word counts at line: ", i, "= ", word_counts[i])
        length += word_counts[i]
        lengths.append(word_counts[i])
        temp.append(lyrics[i])
    else:
        if (count != 0):
            index = (2*(i-count)) - 1 - count2
            print("index: ", index)
            range_length = ranges[index+1] - ranges[index] + 1
            #print("number of words in range diff: ", range_length)
            difference = range_length - length - len(lengths)
            print("difference: ", difference)
            #print("number of wrong in between: ", count, "index: ", index)
            #print("ranges: ", ranges[index])



            if (difference != 0):
                count2 += len(lengths)
            else:
                for line_len in lengths:
                    count3 += 1
                    print("same size!")
                    print("adding i: ", i - count3)
                    perfects.append(i - count3)
                    print("adding to ranges: ", ranges[index] + 1 + last_range)
                    ranges.append(ranges[index] + 1 + last_range)
                    print("adding to ranges: ", ranges[index] + line_len + last_range)
                    ranges.append(ranges[index] + line_len + last_range)
                    last_range += line_len
                    count2 += 1
            
            adder = 0
            count2 += count
            temp = []
            lengths = []
            
        last_range = 0 
        length = 0
        concurrent = False
        count = 0
        count3 = 0
    

ranges.sort()
#for i in range(len(lyrics)):
    #if (i not in perfects):
        #perfects.append(i)

perfects.sort()
print("NEW PERFECTS: ", perfects)

print("NEW RANGES: ", ranges)
# if ranges[] is not divisible by two something has gone wrong
print("NEW RANGES LEN/2: ", int(len(ranges)/2))
print("NEW PERFECTS LEN: ", len(perfects))



count = 0
count2 = 0
count3 = 0
index = 0
perfect_subs = []
to_be_added = []
for i in range(int(len(ranges))):
    count += 1
    if (count % 2 == 0):  
        count3 = 0
        count2 += 1
        for j in range(ranges[i-1], ranges[i]+1):
            to_be_added.append(j)

#print(estimated)
#perfect_subs = srt.compose(perfect_subs)
#print(perfect_subs)
#cleaned = srt.compose(cleaned, reindex=True)
#print(cleaned)


def underliner(start, end, string):
    s = list(string)
    s2 = []
    for i in range(len(s)):
        if (i == start):
            s2.append('<u>')
        if (i == end):
            s2.append('</u>')
        s2.append(s[i])
    return("".join(s2))


print("to_be_addeds: ", to_be_added)
syllables_to_be_added = []
lower = 0
upper = 1
start = 0
end = 0
count = 0
count2 = 0
skipped = []
line_num = 0
line_num2 = 0
flag = 0
flag2 = 1
vector = 0
difference = 0
# CLEAN ranges[] for work done
temp = []


for i in range(len(estimated)):
    tempo = []
    word_pos = 0

    for j in range(syllables[i]):
        last = i == len(estimated) -1
        if (i in to_be_added or last == True):
            if (flag == 1):
                #line_num += 1
                print("MISSED LINE(S)")
                count3 = 0
                if (last == False):
                    print("for loop values: ", perfects[line_num], perfects[line_num+1])
                    for k in range(perfects[line_num] + 1, perfects[line_num+1]):
                        line_num2 += 1
                        print(k)
                        skipped.append(k)

                else:
                    print(len(lyrics) - 1)
                    skipped.append(len(lyrics) -1)
                    break
                #missed_lines.append(line_num)
            nothing = 0
            syllables_to_be_added.append(count)
            
            
            flag = 0
        else:
            flag = 1
            

        if (i >= ranges[lower] and i <= ranges[upper]):
            nothing = 0
        elif (flag != 1):
            temp = []
            count3 = 0
            word_len = 0
            vector = 0
            print("well met", line_num2)
            print()
            print("-----------------------")
            print()
            line_num += 1
            line_num2 += 1
            flag2 = 1
            lower += 2
            upper += 2


        try:
            line = lyrics[perfects[line_num]]
            #print(line_num2)
            if (flag2 == 1):
                for char in line:
                    word_pos += 1
                    if (char == " " or char == "\n"):
                        temp.append(word_pos)
                        #print(word_pos)
                        #print("wahuu")
                        word_pos = 0
                #print("got real lengths of words: ", temp)
                flag2 = 0
                line = lyrics[perfects[line_num]]
                
            
            ##print(" slice of real lyric line: ", perfects[line_num])
            tempo.append(len(cleaned[count].content))
            if (len(tempo) == syllables[i]):
                tempo[0] = tempo[0] - 1
                ##print(tempo, estimated[i], " is word @ ", count3)
                ##print(temp)

                

                # kirjanmerkki ## = importants
                word_len = 0
                for x in range(len(tempo)):
                    word_len += tempo[x]
                    cleaned[count-x].content = line
                    #cleaned[count-x].proprietary = "yes"
                    ##print(cleaned[count-x])
                ##print("syllables: ", word_len, "original: ", temp[count3])

                #!line = lyrics[perfects[line_num]]
                #print(line)
                #!difference = temp[count3] - word_len
                ##if (word_len > temp[count3]):
                    ##print("SYLLABLES LONGER")
                ##elif (word_len == temp[count3]):
                    #print("SAME SIZE")
                #else:
                    ##print("ORIGINAL LONGER")
                #!for x in range(len(tempo)):
                    #!if (tempo[x] == max(tempo)):
                        #!tempo[x] = tempo[x] + difference
                    #!vector += tempo[x]
                    ##print(underliner(start, vector, line))
                    ##print(vector)
                    #!cleaned[count-(len(tempo)-x)].content = underliner(start, vector, line)
                    
                #print(word_len)
                count3 += 1
                
            #line = lyrics[perfects[line_num]]
            #cleaned[count].content = line
            #print(cleaned[count])
        except Exception as e:
            print("error, line_num: ", line_num, e)
        ##print("i: ", i)

        ##print("sub slice: ", count)
        count += 1
    #if(flag == 1):
        #print("asd")

subs = []
bogus = []
#for i in range(len(cleaned)):
    #print((cleaned[i].content).rstrip("\n"), cleaned[i].start, cleaned[i].end)

    #if (cleaned[i].end - cleaned[i].start > timedelta(seconds=2.5)):
        #print("bad")
        #bogus.append(i)

    #if (i not in bogus):
        #subs.append(cleaned[i])

#print(bogus)



print(syllables_to_be_added)
print(skipped)

#cleaned = list(srt.parse(cleaned))
cleaned = srt.compose(cleaned, reindex=True)
print(cleaned)
#subs = srt.compose(subs, reindex=True)

with open ('subs.srt', 'w+', encoding="utf-8") as subtitle_file:
    subtitle_file.write(cleaned)

print(subs)
#print(temp)



