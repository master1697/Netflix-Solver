import os
import csv
import logging
from models import Movie
from app import db

class DataLoader:
    """Load movie data from Netflix CSV dataset"""
    
    def __init__(self):
        self.csv_file = 'netflix_titles.csv'
    
    def load_netflix_data(self):
        """Load Netflix content from CSV file"""
        try:
            if not os.path.exists(self.csv_file):
                logging.error(f"Netflix CSV file not found: {self.csv_file}")
                return
                
            logging.info("Loading Netflix content from CSV...")
            loaded_count = 0
            
            with open(self.csv_file, 'r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                
                for row in csv_reader:
                    try:
                        # Check if content already exists
                        existing_content = Movie.query.filter_by(show_id=row['show_id']).first()
                        if existing_content:
                            continue
                        
                        # Create new content entry
                        content = Movie()
                        content.show_id = row['show_id']
                        content.content_type = row['type']
                        content.title = row['title']
                        content.director = row['director'] if row['director'] else None
                        content.cast = row['cast'] if row['cast'] else None
                        content.country = row['country'] if row['country'] else None
                        content.date_added = row['date_added'] if row['date_added'] else None
                        content.release_year = int(row['release_year']) if row['release_year'] and row['release_year'].isdigit() else None
                        content.rating = row['rating'] if row['rating'] else None
                        content.duration = row['duration'] if row['duration'] else None
                        content.listed_in = row['listed_in'] if row['listed_in'] else None
                        content.description = row['description'] if row['description'] else None
                        
                        db.session.add(content)
                        loaded_count += 1
                        
                        # Commit in batches to avoid memory issues
                        if loaded_count % 100 == 0:
                            db.session.commit()
                            logging.info(f"Loaded {loaded_count} Netflix titles...")
                    
                    except Exception as e:
                        logging.error(f"Error processing row {row.get('show_id', 'unknown')}: {str(e)}")
                        continue
                
                # Final commit
                db.session.commit()
                logging.info(f"Successfully loaded {loaded_count} Netflix titles")
                
        except Exception as e:
            logging.error(f"Error loading Netflix data: {str(e)}")
            db.session.rollback()