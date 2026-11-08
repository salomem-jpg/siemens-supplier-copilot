"""Optional, read-only Snowflake data adapter template.

NOT connected or deployed to Siemens. The SQLite/JSON demo is the default.
This module only queries allowlisted views, with bind parameters for supplier_id.
IT must approve the view schema, credentials, network and access policy first.
"""
import os
import re
from collections.abc import Mapping

VIEW_ALIASES={
    'risk':'SCP_V_SUPPLIER_RISK',
    'performance':'SCP_V_SUPPLIER_PERFORMANCE',
    'evaluation':'SCP_V_SUPPLIER_EVALUATION',
    'relationships':'SCP_V_SUPPLIER_RELATIONSHIP',
}
IDENTIFIER=re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')

def env_identifier(name:str):
    value=os.environ[name]
    if not IDENTIFIER.fullmatch(value):raise ValueError(f'Invalid Snowflake identifier for {name}')
    return value

def get_connector():
    # dependency deliberately optional: install snowflake-connector-python on an approved machine
    import snowflake.connector  # type: ignore
    required=['SCP_SNOWFLAKE_ACCOUNT','SCP_SNOWFLAKE_USER','SCP_SNOWFLAKE_WAREHOUSE','SCP_SNOWFLAKE_DATABASE','SCP_SNOWFLAKE_SCHEMA','SCP_SNOWFLAKE_ROLE']
    if any(not os.getenv(k) for k in required):raise RuntimeError('Snowflake environment / approved credentials not configured')
    # Key-pair auth preferred for enterprises; password included only as an optional local template
    params=dict(account=os.environ['SCP_SNOWFLAKE_ACCOUNT'],user=os.environ['SCP_SNOWFLAKE_USER'],
         warehouse=env_identifier('SCP_SNOWFLAKE_WAREHOUSE'),database=env_identifier('SCP_SNOWFLAKE_DATABASE'),
         schema=env_identifier('SCP_SNOWFLAKE_SCHEMA'),role=env_identifier('SCP_SNOWFLAKE_ROLE'),
         login_timeout=10,network_timeout=15,client_session_keep_alive=False)
    if os.getenv('SCP_SNOWFLAKE_TOKEN'):
        params.update(authenticator='oauth',token=os.environ['SCP_SNOWFLAKE_TOKEN'])
    elif os.getenv('SCP_SNOWFLAKE_PASSWORD'):
        params['password']=os.environ['SCP_SNOWFLAKE_PASSWORD']
    else:raise RuntimeError('Provide an approved OAuth token or a credential configured by IT')
    return snowflake.connector.connect(**params)

def fetch_supplier(supplier_id:str)->dict:
    if not supplier_id or len(supplier_id)>128:raise ValueError('Invalid supplier ID')
    output={'supplier_id':supplier_id,'data_source':'LIVE SNOWFLAKE · unvalidated integration'}
    schema=env_identifier('SCP_SNOWFLAKE_SCHEMA');database=env_identifier('SCP_SNOWFLAKE_DATABASE')
    with get_connector() as conn:
        for key,view in VIEW_ALIASES.items():
            # Identifiers are static or validated, values are bound parameters.
            sql=f'SELECT * FROM "{database}"."{schema}"."{view}" WHERE SUPPLIER_ID = %s LIMIT 1'
            cur=conn.cursor()
            try:
                cur.execute(sql,(supplier_id,)); columns=[d[0].lower() for d in cur.description]; row=cur.fetchone()
                output[key]=dict(zip(columns,row)) if row else None
            finally:cur.close()
    return output
