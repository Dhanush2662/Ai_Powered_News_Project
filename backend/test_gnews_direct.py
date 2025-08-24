import httpx
import asyncio

async def test_gnews():
    api_key = "bb4c445a0ffd965e933b811b0deae819"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            'https://gnews.io/api/v4/top-headlines',
            params={
                'apikey': api_key,
                'country': 'us',
                'max': 5,
                'lang': 'en'
            }
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
        if response.status_code != 200:
            print("\n❌ GNews API Error Details:")
            print(f"Headers: {dict(response.headers)}")
            print(f"Full Response: {response.text}")

if __name__ == "__main__":
    asyncio.run(test_gnews())