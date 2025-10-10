import requests
import time
import json
import os
from typing import Any, Optional, Dict, List
from datetime import datetime
import kevinlulee as kx


class ResilientRequestHandler:
    """
    Generic base class for resilient API requests with disk persistence.
    Can be stopped and resumed based on checkpoint files.
    """
    
    def __init__(
        self,
        total_items: int,
        delay: float = 0.5,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        """
        Args:
            total_items: Total number of items to fetch
            delay: Delay between successful requests (seconds)
            max_retries: Maximum retry attempts per item
            retry_delay: Delay between retries (seconds)
        """
        self.total_items = total_items
        self.checkpoint_file = os.path.expanduser('~/scratch/checkpoint.json')
        self.delay = delay
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        self.results = []
        self.failed_items = []
        self.current_index = 1
        self.completed = False
        
        self._load_checkpoint()
    
    def fetch_item(self, index: int) -> Any:
        """
        Override this method in subclasses to implement specific fetch logic.
        
        Args:
            index: Item index to fetch
            
        Returns:
            Fetched data
        """
        raise NotImplementedError("Subclasses must implement fetch_item()")
    
    def run(self, auto_save_interval: int = 10) -> List[Any]:
        """
        Execute requests, saving checkpoints periodically.
        
        Args:
            auto_save_interval: Save checkpoint every N items
            
        Returns:
            List of successfully fetched results
        """
        print(f"Starting from index {self.current_index}/{self.total_items}...")
        print(f"Already completed: {len(self.results)} items\n")
        
        try:
            while self.current_index <= self.total_items:
                success = self._fetch_with_retry(self.current_index)
                
                if success:
                    if self.current_index % 10 == 0:
                        print(f"Progress: {self.current_index}/{self.total_items} "
                              f"({len(self.results)} successful, {len(self.failed_items)} failed)")
                    
                    # Auto-save checkpoint
                    if self.current_index % auto_save_interval == 0:
                        self._save_checkpoint()
                    
                    time.sleep(self.delay)
                
                self.current_index += 1
            
            self._finalize()
            
        except KeyboardInterrupt:
            print("\n\nInterrupted! Saving checkpoint...")
            self._save_checkpoint()
            print(f"Progress saved. Resume later by running the same script.")
            raise
        
        return self.results
    
    def _fetch_with_retry(self, index: int) -> bool:
        """Attempt to fetch an item with retries."""
        for attempt in range(self.max_retries):
            try:
                result = self.fetch_item(index)
                self.results.append(result)
                return True
                
            except Exception as e:
                if attempt < self.max_retries - 1:
                    print(f"Error at index {index} (attempt {attempt + 1}/{self.max_retries}): {e}")
                    time.sleep(self.retry_delay)
                else:
                    print(f"Failed to fetch index {index} after {self.max_retries} attempts: {e}")
                    self.failed_items.append(index)
                    return False
        
        return False
    
    def _save_checkpoint(self):
        """Save current progress to disk."""
        checkpoint = {
            'timestamp': datetime.now().isoformat(),
            'current_index': self.current_index,
            'total_items': self.total_items,
            'results': self.results,
            'failed_items': self.failed_items,
            'completed': self.completed
        }
        
        with open(self.checkpoint_file, 'w') as f:
            json.dump(checkpoint, f, indent=2)
        
        print(f"Checkpoint saved to {self.checkpoint_file}")
    
    def _load_checkpoint(self):
        """Load progress from disk if checkpoint exists."""
        if os.path.exists(self.checkpoint_file):
            try:
                with open(self.checkpoint_file, 'r') as f:
                    checkpoint = json.load(f)
                
                self.current_index = checkpoint['current_index']
                self.results = checkpoint['results']
                self.failed_items = checkpoint['failed_items']
                self.completed = checkpoint.get('completed', False)
                
                print(f"Loaded checkpoint from {checkpoint['timestamp']}")
                print(f"Resuming from index {self.current_index}")
                
            except Exception as e:
                print(f"Error loading checkpoint: {e}")
                print("Starting fresh...")
        else:
            print("No checkpoint found. Starting fresh...")
    
    def _finalize(self):
        """Mark completion and save final state."""
        self.completed = True
        self._save_checkpoint()
        
        print(f"\n{'='*50}")
        print(f"Fetch completed!")
        print(f"Total items: {self.total_items}")
        print(f"Successfully fetched: {len(self.results)}")
        print(f"Failed: {len(self.failed_items)}")
        if self.failed_items:
            print(f"Failed indices: {self.failed_items}")
        print(f"{'='*50}\n")
    
    def retry_failed(self) -> List[Any]:
        """Retry fetching all failed items."""
        if not self.failed_items:
            print("No failed items to retry.")
            return self.results
        
        print(f"Retrying {len(self.failed_items)} failed items...")
        failed_copy = self.failed_items.copy()
        self.failed_items = []
        
        for index in failed_copy:
            self._fetch_with_retry(index)
        
        self._save_checkpoint()
        print(f"Retry complete. Success: {len(self.results)}, Failed: {len(self.failed_items)}")
        return self.results
    
    def reset(self):
        """Clear checkpoint and start over."""
        if os.path.exists(self.checkpoint_file):
            os.remove(self.checkpoint_file)
        self.results = []
        self.failed_items = []
        self.current_index = 1
        self.completed = False
        print("Checkpoint cleared. Ready to start fresh.")


class PokemonFetcher(ResilientRequestHandler):
    """
    Pokemon-specific implementation of ResilientRequestHandler.
    Fetches data for Pokemon from PokeAPI.
    """
    
    base_url = "https://pokeapi.co/api/v2/pokemon"

    def __init__(
        self,
        total_items: int = 150,
        checkpoint_file: str = "pokemon_checkpoint.json",
    ):
        super().__init__(total_items)
    
    def fetch_item(self, index: int) -> Dict[str, Any]:
        """Fetch a single Pokemon's data."""
        url = f"{self.base_url}/{index}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        return {
            'id': data['id'],
            'name': data['name'].capitalize(),
            'height': data['height'],
            'weight': data['weight'],
            'types': [t['type']['name'] for t in data['types']],
            'abilities': [a['ability']['name'] for a in data['abilities']],
            'stats': {stat['stat']['name']: stat['base_stat'] 
                     for stat in data['stats']},
            'sprite': data['sprites']['front_default']
        }
    


# Example usage
if __name__ == "__main__.fetch_data":
    # Create Pokemon fetcher
    fetcher = PokemonFetcher(
        total_items=150,
    )
    
    # Run the fetch (can be interrupted with Ctrl+C and resumed later)
    pokemon_data = fetcher.run()
    
    # If there were failures, retry them
    if fetcher.failed_items:
        fetcher.retry_failed()
    
    kx.writefile('~/data/pokemon.json', fetcher.results)
    
    # Display first 3 Pokemon as examples
    print("\nSample data:")
    for pokemon in pokemon_data[:3]:
        print(f"\n{pokemon['name']} (#{pokemon['id']})")
        print(f"  Types: {', '.join(pokemon['types'])}")
        print(f"  HP: {pokemon['stats']['hp']}, Attack: {pokemon['stats']['attack']}")


import requests
import os
from pathlib import Path
import time

def fetch_svgs():
    # Create the directory if it doesn't exist
    save_dir = Path.home() / "data" / "pokemon" / "svgs"
    save_dir.mkdir(parents=True, exist_ok=True)
    
    # Base URL for raw GitHub content
    base_url = "https://raw.githubusercontent.com/jnovack/pokemon-svg/master/svg"
    
    # Download Pokemon 1-150
    successful = 0
    failed = []
    
    for i in range(1, 151):
        url = f"{base_url}/{i}.svg"
        filepath = save_dir / f"{i}.svg"
    
        try:
            response = requests.get(url, timeout=10)
    
            if response.status_code == 200:
                with open(filepath, "wb") as f:
                    f.write(response.content)
                successful += 1
                print(f"✓ Downloaded {i}.svg")
            else:
                failed.append(i)
                print(f"✗ Failed to download {i}.svg (Status: {response.status_code})")
    
        except Exception as e:
            failed.append(i)
            print(f"✗ Error downloading {i}.svg: {e}")
    
        # Small delay to be respectful to the server
        time.sleep(0.1)
    
    print(f"\n{'='*50}")
    print(f"Download complete!")
    print(f"Successful: {successful}/150")
    print(f"Failed: {len(failed)}")
    if failed:
        print(f"Failed IDs: {failed}")
    print(f"Saved to: {save_dir}")

if __name__ == "__main__.fetch_svgs":
    fetch_svgs()
