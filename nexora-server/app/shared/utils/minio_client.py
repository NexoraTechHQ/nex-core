def upload_files_to_minio(bucket, tenant_id, files):
    from minio import Minio
    client = Minio("localhost:9000", access_key="minioadmin",
                   secret_key="minioadmin", secure=False)

    bucket_path = f"nexora/{tenant_id}/images/{bucket}"
    if not client.bucket_exists(bucket):
        client.make_bucket(bucket)

    urls = []
    for f in files:
        filename = secure_filename(f.filename)
        full_path = f"{bucket_path}/{filename}"
        client.put_object(bucket, full_path, f.stream,
                          length=-1, part_size=10*1024*1024)
        url = f"http://localhost:9000/{bucket}/{full_path}"
        urls.append(url)
    return urls
