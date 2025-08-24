import httpx
import asyncio

async def test_currents():
    api_key = "0YBdZ4qNfz1fvozauYjQjB_mcfh71oYjyfET1FYTIjPWnf5a"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            'https://api.currentsapi.services/v1/latest-news',
            params={
                'apiKey': api_key,
                'country': 'us',
                'language': 'en'
            }
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
        if response.status_code != 200:
            print("\n❌ Currents API Error Details:")
            print(f"Headers: {dict(response.headers)}")
            print(f"Full Response: {response.text}")

if __name__ == "__main__":
    asyncio.run(test_currents())