from argparse import ArgumentParser

from PIL import Image, ImageFile, ImageOps
from os import mkdir, listdir, remove, removedirs
from requests import get

ImageFile.LOAD_TRUNCATED_IMAGES = True
manga_site_url = "https://scansmangas.xyz/scans"

class NotFoundException(Exception):
    def __init__(self, message:str, page: int) -> None:
        super().__init__(message)
        self.page = page
    
    def get_page(self) -> int:
        return self.page

def convert_int(number: int, max_number: int= 2) -> str:
    if(number < 10**(max_number-1)) :
        return f'0{number}'
    return str(number) 
    

def get_jpg_file_and_next(manga: str, scan_number: int, page_number: int) :
    response = get(f"{manga_site_url}/{manga}/{scan_number}/{page_number}.jpg")

    if response.status_code == 200 :
        file = open(f"output/{manga}/Scan {convert_int(scan_number)}/Page {convert_int(page_number)}.jpg", "wb")
        file.write(response.content)
        file.close()
        get_jpg_file_and_next(manga, scan_number, page_number+1)
    
    if response.status_code == 404 :
        raise NotFoundException(f"Page {page_number} not found", page_number)
    
    else :
        print(response.status_code)

def merge_jpg_to_pdf(manga: str, scan_per_file: int, scan_end: int) -> None :
    scan_start = 16
    scan_index = 0
    while scan_end > scan_start + scan_index  :
        repository = f'Scan {convert_int(scan_start + scan_index)}'
        try :
            first_image = ImageOps.grayscale(Image.open(f'./output/{manga}/{repository}/Page {convert_int(1)}.jpg').convert('RGB'))
        except FileNotFoundError as e :
            scan_index+=1
            continue
        images_to_merge = []
        while scan_index < scan_per_file and scan_end > scan_start + scan_index :
            try: 
                images_to_merge += [ImageOps.grayscale(Image.open(f'./output/{manga}/{repository}/{file_name}').convert('RGB')) for file_name in listdir(f'./{manga}/{repository}')]
            except FileNotFoundError :
                pass
            scan_index+=1
            repository = f'Scan {convert_int(scan_start + scan_index)}'
            
        first_image.save(f'./output/{manga}/{manga} - {convert_int(scan_start)}-{convert_int(scan_start+scan_index-1)}.pdf', save_all=True, append_images=images_to_merge[1:])
        first_image = None
        scan_start += scan_index
        scan_index = 0
    
    
    for repository_index in range(1, scan_end):
        repository = f'Scan {convert_int(repository_index)}'
        for file_name in listdir(f'./output/{manga}/{repository}') :
            remove(f'./output/{manga}/{repository}/{file_name}')
        removedirs(f'./output/{manga}/{repository}')


if __name__ == "__main__" :
    parser = ArgumentParser(description="A program to pick from scansmangas.xyz all jpg files")
    parser.add_argument("--manga", help="the manga wanted")
    parser.add_argument("--agg", help="Aggregation volume per file")

    args = parser.parse_args()
    manga = args._get_kwargs()[1][1]
    scan_per_file = int(args._get_kwargs()[0][1]) if args._get_kwargs()[0][1] else 1
    print(scan_per_file)
    if manga == None:
        raise Exception("A manga name must be precised")
    
    try :
        mkdir(f"output/{manga}")
    except Exception as e:
        mkdir("output")
        
        mkdir(f"output/{manga}")
        
    is_not_over = True
    scan_missing = False 
    scan_number = 0
    while is_not_over :
        try :
            scan_number+=1
            mkdir(f"output/{manga}/Scan {convert_int(scan_number)}")
            print(f"Downloading scan {scan_number}...")
            get_jpg_file_and_next(manga, scan_number, 1)

        except NotFoundException as e:
            if e.get_page() == 1 :
                if not scan_missing :
                    scan_missing = True
                    print(f"Scan {scan_number} is missing")
                else :
                    is_not_over = False
            else :
                print(f"==> Scan {scan_number} completed")
    
    
    merge_jpg_to_pdf(manga=manga, scan_per_file=scan_per_file, scan_end=scan_number-1)
            


