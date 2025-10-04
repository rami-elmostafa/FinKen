def _sb():
    import os
    from supabase import create_client

    #Load environment variables
    from dotenv import load_dotenv
    load_dotenv()

    url = os.environ.get('SUPABASE_URL')
    key = os.environ.get('SUPABASE_ANON_KEY')

    if not url or not key:
        raise RuntimeError("Supabase environment is not configured")
    
    return create_client(url, key)