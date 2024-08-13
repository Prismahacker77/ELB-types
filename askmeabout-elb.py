import boto3

def scan_elbs():
    ec2_client = boto3.client('ec2')
    regions = [region['RegionName'] for region in ec2_client.describe_regions()['Regions']]

    for region in regions:
        print(f"Scanning region: {region}")

        # Classic Load Balancers
        elb_client = boto3.client('elb', region_name=region)
        classic_elbs = elb_client.describe_load_balancers()['LoadBalancerDescriptions']

        for elb in classic_elbs:
            elb_name = elb['LoadBalancerName']
            subnets = elb.get('Subnets', [])
            azs = elb['AvailabilityZones']
            scheme = 'Yes' if elb['Scheme'] == 'internet-facing' else 'No'
            listeners = [(l['Listener']['LoadBalancerPort'], l['Listener']['Protocol']) for l in elb['ListenerDescriptions']]

            print(f"Type: Classic")
            print(f"ELB Name: {elb_name}")
            print(f"Availability Zones: {azs}")
            print(f"Subnets: {subnets}")
            print(f"Internet Facing: {scheme}")
            print(f"Listeners: {listeners}")
            print("-" * 60)

        # Application and Network Load Balancers
        elbv2_client = boto3.client('elbv2', region_name=region)
        modern_elbs = elbv2_client.describe_load_balancers()['LoadBalancers']

        for elb in modern_elbs:
            elb_name = elb['LoadBalancerName']
            elb_type = elb['Type'].capitalize()
            subnets = elb['AvailabilityZones']
            scheme = 'Yes' if elb['Scheme'] == 'internet-facing' else 'No'
            listeners = elbv2_client.describe_listeners(LoadBalancerArn=elb['LoadBalancerArn'])['Listeners']
            listener_info = [(l['Port'], l['Protocol']) for l in listeners]

            print(f"Type: {elb_type}")
            print(f"ELB Name: {elb_name}")
            print(f"Availability Zones & Subnets: {[{'Zone': az['ZoneName'], 'Subnet': az['SubnetId']} for az in subnets]}")
            print(f"Internet Facing: {scheme}")
            print(f"Listeners: {listener_info}")

            # Get the Target Groups associated with the Load Balancer
            target_groups = elbv2_client.describe_target_groups(LoadBalancerArn=elb['LoadBalancerArn'])['TargetGroups']
            
            for tg in target_groups:
                tg_name = tg['TargetGroupName']
                tg_protocol = tg['Protocol']
                tg_port = tg['Port']
                print(f"  Target Group: {tg_name}")
                print(f"    Protocol: {tg_protocol}, Port: {tg_port}")

                # Get the registered targets for the target group
                targets = elbv2_client.describe_target_health(TargetGroupArn=tg['TargetGroupArn'])['TargetHealthDescriptions']
                
                for target in targets:
                    instance_id = target['Target']['Id']
                    target_state = target['TargetHealth']['State']
                    print(f"    Registered Target: {instance_id} (State: {target_state})")
            
            print("-" * 60)

if __name__ == "__main__":
    scan_elbs()
