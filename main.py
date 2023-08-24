from utills import *
from utills_hugging_face import *
from glob import glob
from munch import DefaultMunch
from tqdm import tqdm

def create_pod_text(args):
    create_episode_description(args.pdf_dir_path, args.output_dir)

    papers_paths = glob(f'{args.pdf_dir_path}/*.pdf')
    print('uploading papers')
    papers_api = [upload_paper(p) for p in tqdm(papers_paths)]
    print(papers_paths, papers_api)

    intreduction_text = read_file(args.intreduction_tamplate_path)
    overview_text = create_overview(args.pdf_dir_path,args.overview_tamplate_path,papers_api)
    deepdive_text = create_deep_dive(args.pdf_dir_path,args.deepdive_tamplate_path,papers_api)
    finish_text = read_file(args.finish_tamplate_path)

    with open(f'{args.output_dir}/intreduction.txt','w') as f:
        f.write(intreduction_text)

    pod_text = overview_text + deepdive_text + finish_text

    print('--------------------\n' + pod_text)
    with open(f'{args.output_dir}/main.txt','w',encoding="utf-8") as f:
        f.write(pod_text)
    try:
        os.mkdir(f'{args.output_dir}/split_text')
    except:
        print('already has')
    split_text_file(f'{args.output_dir}/main.txt',f'{args.output_dir}/split_text')
    print('finished')
    print('deleting papers')
    for i in papers_api:
        delete_paper(i)
    print('finished deleting papers')
    return intreduction_text+pod_text

def create_speech_pod(pod_dir):
    try:
        os.mkdir(f'{pod_dir}/speech')
    except:
        print('already has')
    main_text = sorted(glob(f'{pod_dir}/split_text/*.txt'))
    #intreduction_text = read_file(f'{pod_dir}/intreduction.txt')
    for m_t in tqdm(main_text):
        create_speech(read_file(m_t),f'{pod_dir}/speech/{m_t.split("/")[-1].split(".")[0]}.mp3')
    #create_speech(intreduction_text,f'{pod_dir}/speech/intreduction.mp3')

args = {
    'pdf_dir_path': 'papers/25.8',
    'intreduction_tamplate_path': 'templates/intreduction.txt',
    'overview_tamplate_path': 'templates/overview.txt',
    'deepdive_tamplate_path': 'templates/deepdive.txt',
    'finish_tamplate_path': 'templates/finish.txt',
    'output_dir': 'pod_episodes/10'

}
args = DefaultMunch.fromDict(args)

#split_text_file('pod_episodes/10/main.txt','pod_episodes/10/split_text')
#create_pod_text(args)

#download_papers_between_dates('papers/27.7','2023-07-24','2023-07-27')

create_speech_pod(args.output_dir)

